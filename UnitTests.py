import unittest

class TestProjectDocumentRoundtrip(unittest.TestCase):
    def test_project_document_roundtrip(self):
        import json
        from _dataclasses import ProjectDocument, GridConfig, LabelWidgetData, EntryWidgetData, ButtonWidgetData, IdCounters

        #reset counters
        IdCounters.label = IdCounters.entry = IdCounters.button = 1

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

        #add 3 widgets to project document
        widget_1 = LabelWidgetData(x=50, y=50, bg="#111111", fg="#aaaaaa", text="Roundtrip Test")
        widget_1.create_id()
        widget_2 = EntryWidgetData(x=50, y=100, bg="#222222", fg="#bbbbbb")
        widget_2.create_id()
        widget_3 = ButtonWidgetData(x=50, y=150, bg="#333333", fg="#cccccc", text="Roundtrip Test")
        widget_3.create_id()
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

        #check widgets restored
        self.assertEqual(len(new_project_document.widget_models), 3)
        types = [model.type for model in new_project_document.widget_models]
        self.assertEqual(types, ["Label", "Entry", "Button"])

        #check id counters advanced
        self.assertGreaterEqual(IdCounters.label, 2)
        self.assertGreaterEqual(IdCounters.entry, 2)
        self.assertGreaterEqual(IdCounters.button, 2)

class TestAddWidgetFromModel(unittest.TestCase):
    def test_add_widget_from_model(self):
        import tkinter as tk
        from AppState import AppState
        from _dataclasses import ProjectDocument, LabelWidgetData, IdCounters
        from _managers import WidgetView, WidgetController

        root = tk.Tk()
        root.withdraw()
        canvas = tk.Canvas(root, width=300, height=200)
        project_document = ProjectDocument(width=300, height=200, theme={})
        app_state = AppState(project_document)

        IdCounters.label = 1

        widget_view = WidgetView(
            canvas=canvas
        )

        widget_controller = WidgetController(
            app_state=app_state,
            widget_view=widget_view
        )

        model = LabelWidgetData(x=50, y=50, bg="#111111", fg="#aaaaaa", text="Add Widget Test")
        model.create_id()
        app_state.add_widget(model)

        preview_widget, preview_widget_id = widget_view.create_preview_widget(model)
        preview_widget.config(text=model.text, bg=model.bg, fg=model.fg)
        preview_widget.update_idletasks()
        model.width = preview_widget.winfo_reqwidth()
        model.height = preview_widget.winfo_reqheight()
        canvas.delete(preview_widget_id)

        widget_controller.render_soft(model.id)
        widget_id = widget_view.get_widget_id_from_model_id(model.id)

        self.assertIn(widget_id, widget_view.widget_map)
        self.assertEqual(widget_view.widget_map[widget_id]["model"].id, "label1")
        self.assertIsNotNone(model.width)
        self.assertIsNotNone(model.height)

class TestMoveWidget(unittest.TestCase):
    def test_move_widget(self):
        import tkinter as tk
        from AppState import AppState
        from _dataclasses import ProjectDocument, LabelWidgetData, IdCounters
        from _managers import WidgetView, WidgetController

        root = tk.Tk()
        root.withdraw()
        canvas = tk.Canvas(root, width=300, height=200)
        project_document = ProjectDocument(width=300, height=200, theme={})
        app_state = AppState(project_document)

        IdCounters.label = 1

        widget_view = WidgetView(
            canvas=canvas
        )

        widget_controller = WidgetController(
            app_state=app_state,
            widget_view=widget_view
        )

        model = LabelWidgetData(x=50, y=50, bg="#111111", fg="#aaaaaa", text="Move Widget Test")
        model.create_id()
        app_state.add_widget(model)

        widget_controller.render_soft(model.id)
        widget_id = widget_view.get_widget_id_from_model_id(model.id)

        #move by dx/dy
        app_state.move_widget_by(model, 50, 50)
        widget_controller.render_soft(model.id)
        self.assertEqual(model.x, 100)
        self.assertEqual(model.y, 100)

        #move to
        app_state.move_widget_to(model, 150, 150)
        widget_controller.render_soft(model.id)
        self.assertEqual(model.x, 150)
        self.assertEqual(model.y, 150)

        #check if canvas coords updated
        x, y = canvas.coords(widget_id)
        self.assertEqual(x, 150)
        self.assertEqual(y, 150)

class TestUndoRedoMoveWidget(unittest.TestCase):
    def test_undo_redo_move_widget(self):
        import tkinter as tk
        from AppState import AppState
        from _dataclasses import ProjectDocument, LabelWidgetData, IdCounters
        from _managers import WidgetView, WidgetController
        from _commands import CommandStack, MoveWidgets

        root = tk.Tk()
        root.withdraw()
        canvas = tk.Canvas(root, width=300, height=200)
        project_document = ProjectDocument(width=300, height=200, theme={})
        app_state = AppState(project_document)

        IdCounters.label = 1

        widget_view = WidgetView(
            canvas=canvas
        )

        widget_controller = WidgetController(
            app_state=app_state,
            widget_view=widget_view
        )

        model = LabelWidgetData(x=50, y=50, bg="#111111", fg="#aaaaaa", text="Move Widget Test")
        model.create_id()
        app_state.add_widget(model)

        widget_controller.render_soft(model.id)

        command_stack = CommandStack()

        #move by dx/dy
        command_stack.execute(MoveWidgets(frozenset({model.id}), 50, 50, widget_view, widget_controller))
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
        import tkinter as tk
        from AppState import AppState
        from _dataclasses import ProjectDocument, LabelWidgetData, IdCounters
        from _managers import WidgetView, WidgetController
        from _commands import CommandStack, MoveWidgetsTo

        root = tk.Tk()
        root.withdraw()
        canvas = tk.Canvas(root, width=300, height=200)
        project_document = ProjectDocument(width=300, height=200, theme={})
        app_state = AppState(project_document)

        IdCounters.label = 1

        widget_view = WidgetView(
            canvas=canvas
        )

        widget_controller = WidgetController(
            app_state=app_state,
            widget_view=widget_view
        )

        model = LabelWidgetData(x=50, y=50, bg="#111111", fg="#aaaaaa", text="Move Widget Test")
        model.create_id()
        app_state.add_widget(model)

        widget_controller.render_soft(model.id)

        command_stack = CommandStack()
        command = MoveWidgetsTo(frozenset({model.id}), widget_view, widget_controller)

        #simulate drag preview
        command.preview_move(50, 50)
        self.assertEqual(model.x, 100)
        self.assertEqual(model.y, 100)

        #commit
        command.freeze_final_positions()
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

if __name__ == '__main__':
    unittest.main()