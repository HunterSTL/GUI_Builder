import unittest

class TestProjectDocumentRoundtrip(unittest.TestCase):
    def test_project_document_roundtrip(self):
        import json
        from model import ProjectDocument, GridConfig, LabelWidgetData, EntryWidgetData, ButtonWidgetData
        from utility import WidgetType

        #build project document
        project_document = ProjectDocument(
            version=1,
            title="Roundtrip Test",
            width=640,
            height=480,
            icon_path=None,
            grid=GridConfig(
                size=50,
                color="#888888",
                visible = True
            ),
            theme={},
            widget_models=[]
        )

        #add 3 models to project document
        widget_1 = LabelWidgetData(x=50, y=50, bg="#111111", fg="#aaaaaa", text="Roundtrip Test")
        widget_1.create_id(project_document.id_counters)
        widget_2 = EntryWidgetData(x=50, y=100, bg="#222222", fg="#bbbbbb")
        widget_2.create_id(project_document.id_counters)
        widget_3 = ButtonWidgetData(x=50, y=150, bg="#333333", fg="#cccccc", text="Roundtrip Test")
        widget_3.create_id(project_document.id_counters)
        project_document.widget_models.extend([widget_1, widget_2, widget_3])

        #serialize
        blob = json.dumps(project_document.to_json(), ensure_ascii=False, indent=2)

        #deserialize
        data = json.loads(blob)
        new_project_document = ProjectDocument.from_json(data)

        #check basic fields
        self.assertEqual(new_project_document.title, "Roundtrip Test")
        self.assertEqual(new_project_document.width, 640)
        self.assertEqual(new_project_document.height, 480)
        self.assertEqual(new_project_document.grid.size, 50)
        self.assertEqual(new_project_document.grid.color, "#888888")
        self.assertEqual(new_project_document.grid.visible, True)

        #check restoration of models
        self.assertEqual(len(new_project_document.widget_models), 3)
        types = [model.type for model in new_project_document.widget_models]
        self.assertEqual(types, [WidgetType.LABEL, WidgetType.ENTRY, WidgetType.BUTTON])

        #check advancement of ID counters
        self.assertGreaterEqual(project_document.id_counters.label, 2)
        self.assertGreaterEqual(project_document.id_counters.entry, 2)
        self.assertGreaterEqual(project_document.id_counters.button, 2)

class TestAddWidgetFromModel(unittest.TestCase):
    def test_add_widget_from_model(self):
        import tkinter as tk
        from AppState import AppState
        from model import ProjectDocument, LabelWidgetData
        from view import WidgetView

        root = tk.Tk()
        root.withdraw()
        canvas = tk.Canvas(root, width=300, height=200)
        project_document = ProjectDocument(width=300, height=200, theme={})
        app_state = AppState(project_document)

        widget_view = WidgetView(
            canvas=canvas
        )

        model = LabelWidgetData(x=50, y=50, bg="#111111", fg="#aaaaaa", text="Add Widget Test")
        model.create_id(project_document.id_counters)
        app_state.add_model(model)

        model.width, model.height = widget_view.measure_preview_widget(model)

        widget_view.update_widget_for(model)
        widget_id = widget_view.get_widget_id_from_model_id(model.id)

        self.assertIn(widget_id, widget_view.widget_map)
        self.assertEqual(widget_view.widget_map[widget_id]["model"].id, "label_1")
        self.assertIsNotNone(model.width)
        self.assertIsNotNone(model.height)

class TestMoveWidget(unittest.TestCase):
    def test_move_widget(self):
        import tkinter as tk
        from AppState import AppState
        from model import ProjectDocument, LabelWidgetData
        from view import WidgetView

        root = tk.Tk()
        root.withdraw()
        canvas = tk.Canvas(root, width=300, height=200)
        project_document = ProjectDocument(width=300, height=200, theme={})
        app_state = AppState(project_document)

        widget_view = WidgetView(
            canvas=canvas
        )

        model = LabelWidgetData(x=50, y=50, bg="#111111", fg="#aaaaaa", text="Move Widget Test")
        model.create_id(project_document.id_counters)
        app_state.add_model(model)

        widget_view.update_widget_for(model)
        widget_id = widget_view.get_widget_id_from_model_id(model.id)

        #offset position by a delta
        app_state.offset_model_position(model, 50, 50)
        widget_view.update_widget_for(model)
        self.assertEqual(model.x, 100)
        self.assertEqual(model.y, 100)

        #set absolute position
        app_state.set_model_position(model, 150, 150)
        widget_view.update_widget_for(model)
        self.assertEqual(model.x, 150)
        self.assertEqual(model.y, 150)

        #check if canvas coords updated
        x, y = canvas.coords(widget_id)
        self.assertEqual(x, 150)
        self.assertEqual(y, 150)

class TestUndoRedoAddWidget(unittest.TestCase):
    def test_undo_redo_add_widget(self):
        from AppState import AppState
        from model import ProjectDocument, LabelWidgetData
        from commands import CommandStack, AddWidget

        project_document = ProjectDocument(width=300, height=200, theme={})
        app_state = AppState(project_document)

        model = LabelWidgetData(x=50, y=50, bg="#111111", fg="#aaaaaa", text="Add Widget Test")
        model.create_id(project_document.id_counters)
        command_stack = CommandStack()

        #add model
        command_stack.execute(AddWidget(model, app_state))
        self.assertEqual(len(project_document.widget_models), 1)

        #undo
        command_stack.undo()
        self.assertEqual(len(project_document.widget_models), 0)

        #redo
        command_stack.redo()
        self.assertEqual(len(project_document.widget_models), 1)

class TestUndoRedoDeleteWidget(unittest.TestCase):
    def test_undo_redo_delete_widget(self):
        from AppState import AppState
        from model import ProjectDocument, LabelWidgetData
        from commands import CommandStack, DeleteWidgets

        project_document = ProjectDocument(width=300, height=200, theme={})
        app_state = AppState(project_document)

        model = LabelWidgetData(x=50, y=50, bg="#111111", fg="#aaaaaa", text="Delete Widget Test")
        model.create_id(project_document.id_counters)
        app_state.add_model(model)

        command_stack = CommandStack()

        #delete model
        command_stack.execute(DeleteWidgets(tuple([model]), app_state))
        self.assertEqual(len(project_document.widget_models), 0)

        #undo
        command_stack.undo()
        self.assertEqual(len(project_document.widget_models), 1)

        #redo
        command_stack.redo()
        self.assertEqual(len(project_document.widget_models), 0)

class TestUndoRedoMoveWidget(unittest.TestCase):
    def test_undo_redo_move_widget(self):
        from AppState import AppState
        from model import ProjectDocument, LabelWidgetData
        from commands import CommandStack, MoveWidgets

        project_document = ProjectDocument(width=300, height=200, theme={})
        app_state = AppState(project_document)

        model = LabelWidgetData(x=50, y=50, bg="#111111", fg="#aaaaaa", text="Move Widget Test")
        model.create_id(project_document.id_counters)
        app_state.add_model(model)

        command_stack = CommandStack()

        #move by a delta
        command_stack.execute(MoveWidgets(tuple([model]), 50, 50, app_state))
        self.assertEqual(model.x, 100)
        self.assertEqual(model.y, 100)

        #undo then redo
        command_stack.undo()
        self.assertEqual(model.x, 50)
        self.assertEqual(model.y, 50)
        command_stack.redo()
        self.assertEqual(model.x, 100)
        self.assertEqual(model.y, 100)

class TestUndoRedoMoveWidgetTo(unittest.TestCase):
    def test_undo_redo_move_widget_to(self):
        from AppState import AppState
        from model import ProjectDocument, LabelWidgetData
        from commands import CommandStack, MoveWidgetsTo

        project_document = ProjectDocument(width=300, height=200, theme={})
        app_state = AppState(project_document)

        model = LabelWidgetData(x=50, y=50, bg="#111111", fg="#aaaaaa", text="Move Widget Test")
        model.create_id(project_document.id_counters)
        app_state.add_model(model)

        command_stack = CommandStack()
        command = MoveWidgetsTo(tuple([model]), app_state)

        #simulate live dragging
        command.apply_drag_delta(50, 50)
        self.assertEqual(model.x, 100)
        self.assertEqual(model.y, 100)

        #commit
        command.record_final_positions()
        command_stack.execute(command)
        self.assertEqual(model.x, 100)
        self.assertEqual(model.y, 100)

        #undo then redo
        command_stack.undo()
        self.assertEqual(model.x, 50)
        self.assertEqual(model.y, 50)
        command_stack.redo()
        self.assertEqual(model.x, 100)
        self.assertEqual(model.y, 100)

class TestUndoRedoPasteWidget(unittest.TestCase):
    def test_undo_redo_paste_widget(self):
        from AppState import AppState
        from model import ProjectDocument, LabelWidgetData
        from commands import CommandStack, PasteWidgetsFromClipboard

        project_document = ProjectDocument(width=300, height=200, theme={})
        app_state = AppState(project_document)

        model = LabelWidgetData(x=50, y=50, bg="#111111", fg="#aaaaaa", text="Paste Widget Test")
        model.create_id(project_document.id_counters)
        app_state.add_model(model)

        #copy model to clipboard
        clipboard = []
        model_data = model.to_dict(include_id=False)    #exclude ID because pasting creates new IDs, except on redo
        clipboard.append(model_data)

        command_stack = CommandStack()

        #paste model from clipboard
        command_stack.execute(PasteWidgetsFromClipboard(clipboard, app_state))
        self.assertEqual(len(project_document.widget_models), 2)
        self.assertNotEqual(project_document.widget_models[0], project_document.widget_models[1])   #pasted widget has different ID

        #undo
        command_stack.undo()
        self.assertEqual(len(project_document.widget_models), 1)

        #redo
        command_stack.redo()
        self.assertEqual(len(project_document.widget_models), 2)

if __name__ == '__main__':
    unittest.main()
