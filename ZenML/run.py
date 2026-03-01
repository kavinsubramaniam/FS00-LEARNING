from zenml import step, pipeline

@step
def simple_step() -> str:
    """A simple step that returns a string."""
    return "Hello, ZenML!"

@pipeline
def simple_pipeline() -> str:
    """A simple pipeline that runs the simple step."""
    return simple_step()

if __name__ == "__main__":
    simple_pipeline()