
help:
	@echo "# Read the source"

# Build Python package.
build:
	rm -rf build dist
	uv build
	ls -lh dist

# Publish the package
publish: build
	uv publish



