import os
import pytest
import re
from telemetry.report import gist, markdown

@pytest.mark.parametrize(
    "template,fields",
    [
        ('results.template.md',
            ["branch","pr_id","timestamp","direction",
             "triggered_by","commit_sha","commit_date","test_job_name",
             "test_build_number","test_build_status"]
        ),
    ]
)
def test_get_identifiers(template, fields):
    dir = os.path.dirname(os.path.realpath(__file__))
    template_path = os.path.join(dir,"..", "telemetry", "report", "templates", template)
    m = markdown.Markdown(template_path)
    identifiers = m.get_identifiers()
    assert len(identifiers) != 0
    for field in fields:
        assert field in identifiers

@pytest.mark.parametrize(
    "template",
    [
        ('results.template.md'),
    ]
)
def test_substitute(template):
    dir = os.path.dirname(os.path.realpath(__file__))
    template_path = os.path.join(dir,"..", "telemetry", "report", "templates", template)
    m = markdown.Markdown(template_path)

    fields = m.get_identifiers()

    field_dict = {}
    for field in fields:
        field_dict.update({field: f"{field}_test_data"})

    formatted = m.substitute(field_dict)
    assert formatted

    for field in fields:
        assert f"{field}_test_data" in formatted

@pytest.mark.parametrize(
    "template",
    [
        ('results.template.md'),
    ]
)
def test_generate(template):
    
    filename = "test_result_file.md"
    dir = os.path.dirname(os.path.realpath(__file__))
    template_path = os.path.join(dir,"..", "telemetry", "report", "templates", template)
    m = markdown.Markdown(template_path)

    fields = m.get_identifiers()

    field_dict = {}
    for field in fields:
        field_dict.update({field: f"{field}_test_data"})
    
    assert not os.path.exists(filename)
    result_path = m.generate(field_dict, filename)
    assert result_path
    assert os.path.exists(result_path)
    os.remove(result_path)


    