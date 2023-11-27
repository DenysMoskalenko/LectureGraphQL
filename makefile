UVICORN_RUN = uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

run:
	$(UVICORN_RUN)

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
