test:
	coverage run -m pytest
	coverage report

test-html:
	coverage run -m pytest
	coverage report

test-no-coverage:
	pytest

schema:
	strawberry export-schema schema_export:schema > schema.graphql
