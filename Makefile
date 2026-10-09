
help:
	@echo "# Read the source"

# Run the test suite.
test:
	pixi run pytest

# Build Python package.
build:
	rm -rf build dist
	uv build
	ls -lh dist

# Publish the package
publish: build
	uv publish



