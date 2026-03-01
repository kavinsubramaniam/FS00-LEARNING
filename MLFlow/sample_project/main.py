import mlflow
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

mlflow.set_tracking_uri("http://localhost:5000")

# The set_experiment API creates a new experiment if it doesn't exist.
mlflow.set_experiment("Deep Learning Experiment")

# IMPORTANT: Enable system metrics monitoring
mlflow.config.enable_system_metrics_logging()
mlflow.config.set_system_metrics_sampling_interval(1)


# Define device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load and prepare data
transform = transforms.Compose(
    [transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))]
)
train_dataset = datasets.FashionMNIST(
    "data", train=True, download=True, transform=transform
)
test_dataset = datasets.FashionMNIST("data", train=False, transform=transform)
train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=1000)

class NeuralNetwork(nn.Module):
    def __init__(self):
        super().__init__()
        self.flatten = nn.Flatten()
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(28 * 28, 512),
            nn.ReLU(),
            nn.Linear(512, 512),
            nn.ReLU(),
            nn.Linear(512, 10),
        )

    def forward(self, x):
        x = self.flatten(x)
        logits = self.linear_relu_stack(x)
        return logits


model = NeuralNetwork().to(device)

# Training parameters
params = {
    "epochs": 5,
    "learning_rate": 1e-3,
    "batch_size": 64,
    "optimizer": "SGD",
    "model_type": "MLP",
    "hidden_units": [512, 512],
}

# Define optimizer and loss function
loss_fn = nn.CrossEntropyLoss()
optimizer = optim.SGD(model.parameters(), lr=params["learning_rate"])


with mlflow.start_run() as run:
    # Log training parameters
    mlflow.log_params(params)

    for epoch in range(params["epochs"]):
        model.train()
        train_loss, correct, total = 0, 0, 0

        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = data.to(device), target.to(device)

            # Forward pass
            optimizer.zero_grad()
            output = model(data)
            loss = loss_fn(output, target)

            # Backward pass
            loss.backward()
            optimizer.step()

            # Calculate metrics
            train_loss += loss.item()
            _, predicted = output.max(1)
            total += target.size(0)
            correct += predicted.eq(target).sum().item()

            # Log batch metrics (every 100 batches)
            if batch_idx % 100 == 0:
                batch_loss = train_loss / (batch_idx + 1)
                batch_acc = 100.0 * correct / total
                mlflow.log_metrics(
                    {"batch_loss": batch_loss, "batch_accuracy": batch_acc},
                    step=epoch * len(train_loader) + batch_idx,
                )

        # Calculate epoch metrics
        epoch_loss = train_loss / len(train_loader)
        epoch_acc = 100.0 * correct / total

        # Validation
        model.eval()
        val_loss, val_correct, val_total = 0, 0, 0
        with torch.no_grad():
            for data, target in test_loader:
                data, target = data.to(device), target.to(device)
                output = model(data)
                loss = loss_fn(output, target)

                val_loss += loss.item()
                _, predicted = output.max(1)
                val_total += target.size(0)
                val_correct += predicted.eq(target).sum().item()

        # Calculate and log epoch validation metrics
        val_loss = val_loss / len(test_loader)
        val_acc = 100.0 * val_correct / val_total

        # Log epoch metrics
        mlflow.log_metrics(
            {
                "train_loss": epoch_loss,
                "train_accuracy": epoch_acc,
                "val_loss": val_loss,
                "val_accuracy": val_acc,
            },
            step=epoch,
        )
        # Log checkpoint at the end of each epoch
        mlflow.pytorch.log_model(model, name=f"checkpoint_{epoch}")

        print(
            f"Epoch {epoch+1}/{params['epochs']}, "
            f"Train Loss: {epoch_loss:.4f}, Train Acc: {epoch_acc:.2f}%, "
            f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%"
        )

    # Log the final trained model
    model_info = mlflow.pytorch.log_model(model, name="final_model")