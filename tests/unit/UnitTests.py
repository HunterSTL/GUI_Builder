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
        widget_1 = LabelWidgetData(
            id=project_document.id_counters.generate_id(WidgetType.LABEL),
            x=50,
            y=50,
            bg="#111111",
            fg="#aaaaaa",
            text="Roundtrip Test"
        )
        widget_2 = EntryWidgetData(
            id=project_document.id_counters.generate_id(WidgetType.ENTRY),
            x=50,
            y=100,
            bg="#222222",
            fg="#bbbbbb"
        )
        widget_3 = ButtonWidgetData(
            id=project_document.id_counters.generate_id(WidgetType.BUTTON),
            x=50,
            y=150,
            bg="#333333",
            fg="#cccccc",
            text="Roundtrip Test"
        )
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
        from utility import WidgetType
        from view import WidgetView

        root = tk.Tk()
        root.withdraw()
        canvas = tk.Canvas(root, width=300, height=200)
        project_document = ProjectDocument(width=300, height=200, theme={})
        app_state = AppState(project_document)

        widget_view = WidgetView(
            canvas=canvas
        )

        text = "Add Widget Test"
        width, height = widget_view.measure_preview_widget(WidgetType.LABEL, text)
        model = LabelWidgetData(
            id=project_document.id_counters.generate_id(WidgetType.LABEL),
            x=50,
            y=50,
            bg="#111111",
            fg="#aaaaaa",
            width=width,
            height=height,
            text=text
        )
        app_state.add_model(model)


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
        from utility import WidgetType
        from view import WidgetView

        root = tk.Tk()
        root.withdraw()
        canvas = tk.Canvas(root, width=300, height=200)
        project_document = ProjectDocument(width=300, height=200, theme={})
        app_state = AppState(project_document)

        widget_view = WidgetView(
            canvas=canvas
        )

        model = LabelWidgetData(
            id=project_document.id_counters.generate_id(WidgetType.LABEL),
            x=50,
            y=50,
            bg="#111111",
            fg="#aaaaaa",
            text="Move Widget Test"
        )
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
        from utility import WidgetType

        project_document = ProjectDocument(width=300, height=200, theme={})
        app_state = AppState(project_document)

        model = LabelWidgetData(
            id=project_document.id_counters.generate_id(WidgetType.LABEL),
            x=50,
            y=50,
            bg="#111111",
            fg="#aaaaaa",
            text="Add Widget Test"
        )
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
        from utility import WidgetType

        project_document = ProjectDocument(width=300, height=200, theme={})
        app_state = AppState(project_document)

        model = LabelWidgetData(
            id=project_document.id_counters.generate_id(WidgetType.LABEL),
            x=50,
            y=50,
            bg="#111111",
            fg="#aaaaaa",
            text="Delete Widget Test"
        )
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
        from utility import WidgetType

        project_document = ProjectDocument(width=300, height=200, theme={})
        app_state = AppState(project_document)

        model = LabelWidgetData(
            id=project_document.id_counters.generate_id(WidgetType.LABEL),
            x=50,
            y=50,
            bg="#111111",
            fg="#aaaaaa",
            text="Move Widget Test"
        )
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
        from utility import WidgetType

        project_document = ProjectDocument(width=300, height=200, theme={})
        app_state = AppState(project_document)

        model = LabelWidgetData(
            id=project_document.id_counters.generate_id(WidgetType.LABEL),
            x=50,
            y=50,
            bg="#111111",
            fg="#aaaaaa",
            text="Move Widget Test"
        )
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

class TestUndoRedoPasteWidgets(unittest.TestCase):
    def test_undo_redo_paste_widgets(self):
        from AppState import AppState
        from model import ProjectDocument, LabelWidgetData
        from commands import CommandStack, PasteWidgetsFromClipboard
        from utility import WidgetType

        project_document = ProjectDocument(width=300, height=200, theme={})
        app_state = AppState(project_document)

        model_1 = LabelWidgetData(
            id=project_document.id_counters.generate_id(WidgetType.LABEL),
            x=50,
            y=50,
            width=100,
            height=20,
            bg="#111111",
            fg="#aaaaaa",
            text="Paste Widget Test"
        )
        model_2 = LabelWidgetData(
            id=project_document.id_counters.generate_id(WidgetType.LABEL),
            x=50,
            y=100,
            width=100,
            height=20,
            bg="#111111",
            fg="#aaaaaa",
            text="Paste Widget Test"
        )
        app_state.add_model(model_1)
        app_state.add_model(model_2)

        #copy models to clipboard
        clipboard = [model_1.to_dict(include_id=False), model_2.to_dict(include_id=False)]

        command_stack = CommandStack()

        #paste models from clipboard
        command_stack.execute(
            PasteWidgetsFromClipboard(
                clipboard=clipboard,
                dx=50,
                dy=50,
                app_state=app_state
            )
        )

        pasted_model_1 = project_document.widget_models[2]
        pasted_model_2 = project_document.widget_models[3]

        self.assertEqual(len(project_document.widget_models), 4)    #four models in ProjectDocument
        self.assertNotEqual(model_1.id, pasted_model_1.id)          #pasted models have different IDs
        self.assertNotEqual(model_2.id, pasted_model_2.id)
        self.assertEqual(pasted_model_1.x, 100)                     #pasted models are at expected positions
        self.assertEqual(pasted_model_1.y, 100)
        self.assertEqual(pasted_model_2.x, 100)
        self.assertEqual(pasted_model_2.y, 150)
        self.assertEqual(                                           #pasted models are selected
            app_state.get_selected_models(),
            (pasted_model_1, pasted_model_2)
        )
        self.assertEqual(                                           #pasted model 2 is last selected
            app_state.get_last_selected_model_id(),
            pasted_model_2.id
        )

        #undo
        command_stack.undo()
        self.assertEqual(len(project_document.widget_models), 2)    #two models in ProjectDocument

        #redo
        command_stack.redo()
        redone_model_1 = project_document.widget_models[2]
        redone_model_2 = project_document.widget_models[3]
        self.assertEqual(len(project_document.widget_models), 4)    #four models in ProjectDocument
        self.assertEqual(redone_model_1.id, pasted_model_1.id)      #redone models reuse same IDs
        self.assertEqual(redone_model_2.id, pasted_model_2.id)

if __name__ == '__main__':
    unittest.main()
