test:
	pytest

coverage:
	coverage run -m pytest
	coverage report

coverage-html:
	coverage run -m pytest
	coverage html

schema:
	strawberry export-schema schema_export:schema > schema.graphql
