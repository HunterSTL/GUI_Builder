import json

from tests.unit.Framework import assert_equal

from model import ProjectDocument, LabelWidget, EntryWidget, ButtonWidget

def test_project_document_roundtrip() -> None:
    project_document = ProjectDocument()
    widget_1 = LabelWidget(
        x=100,
        y=50,
        bg="#000000",
        fg="#000000",
        width=100,
        height=20,
        text="test",
        id="1"
    )
    widget_2 = EntryWidget(
        x=100,
        y=100,
        bg="#000000",
        fg="#000000",
        width=100,
        height=20,
        id="2"
    )
    widget_3 = ButtonWidget(
        x=100,
        y=150,
        bg="#000000",
        fg="#000000",
        width=100,
        height=20,
        text="test",
        id="3"
    )
    project_document.widgets.extend([widget_1, widget_2, widget_3])
    project_json = json.dumps(project_document.to_dict(), ensure_ascii=False, indent=2)
    project_data = json.loads(project_json)
    new_project_document = ProjectDocument.from_dict(project_data)
    assert_equal(
        actual=new_project_document,
        expected=project_document,
        message="Deserialized ProjectDocument does not match original ProjectDocument"
    )
