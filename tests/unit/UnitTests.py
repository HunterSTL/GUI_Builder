import unittest

class TestProjectDocumentRoundtrip(unittest.TestCase):
    def test_project_document_roundtrip(self):
        import json
        from model import ProjectDocument, GridConfig, LabelWidget, EntryWidget, ButtonWidget
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
            widgets=[]
        )

        #add 3 widgets to project document
        widget_1 = LabelWidget(
            id=project_document.id_counters.generate_id(WidgetType.LABEL),
            x=50,
            y=50,
            bg="#111111",
            fg="#aaaaaa",
            width=100,
            height=20,
            text="Roundtrip Test"
        )
        widget_2 = EntryWidget(
            id=project_document.id_counters.generate_id(WidgetType.ENTRY),
            x=50,
            y=100,
            bg="#222222",
            fg="#bbbbbb",
            width=100,
            height=20
        )
        widget_3 = ButtonWidget(
            id=project_document.id_counters.generate_id(WidgetType.BUTTON),
            x=50,
            y=150,
            bg="#333333",
            fg="#cccccc",
            width=100,
            height=20,
            text="Roundtrip Test"
        )
        project_document.widgets.extend([widget_1, widget_2, widget_3])

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

        #check restoration of widgets
        self.assertEqual(len(new_project_document.widgets), 3)
        types = [widget.type for widget in new_project_document.widgets]
        self.assertEqual(types, [WidgetType.LABEL, WidgetType.ENTRY, WidgetType.BUTTON])

        #check advancement of ID counters
        self.assertGreaterEqual(project_document.id_counters.label, 2)
        self.assertGreaterEqual(project_document.id_counters.entry, 2)
        self.assertGreaterEqual(project_document.id_counters.button, 2)

class TestRenderWidget(unittest.TestCase):
    def test_render_widget(self):
        import tkinter as tk
        from AppState import AppState
        from model import ProjectDocument, LabelWidget
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
        width, height = widget_view.measure_preview_tk_widget(WidgetType.LABEL, text)
        widget = LabelWidget(
            id=project_document.id_counters.generate_id(WidgetType.LABEL),
            x=50,
            y=50,
            bg="#111111",
            fg="#aaaaaa",
            width=width,
            height=height,
            text=text
        )
        app_state.add_widget(widget)

        widget_view.render_tk_widget_for(widget)
        canvas_item_id = widget_view.get_canvas_item_id_from_widget_id(widget.id)

        self.assertIn(canvas_item_id, widget_view.widget_map)
        self.assertEqual(widget_view.widget_map[canvas_item_id]["widget"].id, "label_1")
        self.assertIsNotNone(widget.width)
        self.assertIsNotNone(widget.height)

class TestMoveWidget(unittest.TestCase):
    def test_move_widget(self):
        import tkinter as tk
        from AppState import AppState
        from model import ProjectDocument, LabelWidget
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

        text = "Move Widget Test"
        width, height = widget_view.measure_preview_tk_widget(
            widget_type=WidgetType.LABEL,
            text=text
        )
        widget = LabelWidget(
            id=project_document.id_counters.generate_id(WidgetType.LABEL),
            x=50,
            y=50,
            bg="#111111",
            fg="#aaaaaa",
            width=width,
            height=height,
            text=text
        )
        app_state.add_widget(widget)

        widget_view.render_tk_widget_for(widget)
        canvas_item_id = widget_view.get_canvas_item_id_from_widget_id(widget.id)

        #offset position by a delta
        app_state.offset_widget_position(widget, 50, 50)
        widget_view.render_tk_widget_for(widget)
        self.assertEqual(widget.x, 100)
        self.assertEqual(widget.y, 100)

        #set absolute position
        app_state.set_widget_position(widget, 150, 150)
        widget_view.render_tk_widget_for(widget)
        self.assertEqual(widget.x, 150)
        self.assertEqual(widget.y, 150)

        #check if canvas coords updated
        x, y = canvas.coords(canvas_item_id)
        self.assertEqual(x, 150)
        self.assertEqual(y, 150)

class TestUndoRedoAddWidget(unittest.TestCase):
    def test_undo_redo_add_widget(self):
        from AppState import AppState
        from model import ProjectDocument, LabelWidget
        from commands import CommandStack, AddWidget
        from utility import WidgetType

        project_document = ProjectDocument(width=300, height=200, theme={})
        app_state = AppState(project_document)

        widget = LabelWidget(
            id=project_document.id_counters.generate_id(WidgetType.LABEL),
            x=50,
            y=50,
            bg="#111111",
            fg="#aaaaaa",
            width=100,
            height=20,
            text="Add Widget Test"
        )
        command_stack = CommandStack()

        #add widget
        command_stack.execute(AddWidget(widget, app_state))
        self.assertEqual(len(project_document.widgets), 1)

        #undo
        command_stack.undo()
        self.assertEqual(len(project_document.widgets), 0)

        #redo
        command_stack.redo()
        self.assertEqual(len(project_document.widgets), 1)

class TestUndoRedoDeleteWidget(unittest.TestCase):
    def test_undo_redo_delete_widget(self):
        from AppState import AppState
        from model import ProjectDocument, LabelWidget
        from commands import CommandStack, DeleteWidgets
        from utility import WidgetType

        project_document = ProjectDocument(width=300, height=200, theme={})
        app_state = AppState(project_document)

        widget = LabelWidget(
            id=project_document.id_counters.generate_id(WidgetType.LABEL),
            x=50,
            y=50,
            bg="#111111",
            fg="#aaaaaa",
            width=100,
            height=20,
            text="Delete Widget Test"
        )
        app_state.add_widget(widget)

        command_stack = CommandStack()

        #delete widget
        command_stack.execute(DeleteWidgets(tuple([widget]), app_state))
        self.assertEqual(len(project_document.widgets), 0)

        #undo
        command_stack.undo()
        self.assertEqual(len(project_document.widgets), 1)

        #redo
        command_stack.redo()
        self.assertEqual(len(project_document.widgets), 0)

class TestUndoRedoNudgeWidget(unittest.TestCase):
    def test_undo_redo_nudge_widget(self):
        from AppState import AppState
        from model import ProjectDocument, LabelWidget
        from commands import CommandStack, NudgeWidgets
        from utility import WidgetType

        project_document = ProjectDocument(width=300, height=200, theme={})
        app_state = AppState(project_document)

        widget = LabelWidget(
            id=project_document.id_counters.generate_id(WidgetType.LABEL),
            x=50,
            y=50,
            bg="#111111",
            fg="#aaaaaa",
            width=100,
            height=20,
            text="Nudge Widget Test"
        )
        app_state.add_widget(widget)

        command_stack = CommandStack()

        #nudge by a delta
        command_stack.execute(NudgeWidgets(tuple([widget]), 50, 50, app_state))
        self.assertEqual(widget.x, 100)
        self.assertEqual(widget.y, 100)

        #undo then redo
        command_stack.undo()
        self.assertEqual(widget.x, 50)
        self.assertEqual(widget.y, 50)
        command_stack.redo()
        self.assertEqual(widget.x, 100)
        self.assertEqual(widget.y, 100)

class TestUndoRedoDragWidget(unittest.TestCase):
    def test_undo_redo_drag_widget(self):
        from AppState import AppState
        from model import ProjectDocument, LabelWidget
        from commands import CommandStack, DragWidgets
        from utility import WidgetType

        project_document = ProjectDocument(width=300, height=200, theme={})
        app_state = AppState(project_document)

        widget = LabelWidget(
            id=project_document.id_counters.generate_id(WidgetType.LABEL),
            x=50,
            y=50,
            bg="#111111",
            fg="#aaaaaa",
            width=100,
            height=20,
            text="Drag Widget Test"
        )
        app_state.add_widget(widget)

        command_stack = CommandStack()
        command = DragWidgets(tuple([widget]), app_state)

        #simulate live dragging
        command.apply_drag_delta(50, 50)
        self.assertEqual(widget.x, 100)
        self.assertEqual(widget.y, 100)

        #commit
        command.record_final_positions()
        command_stack.execute(command)
        self.assertEqual(widget.x, 100)
        self.assertEqual(widget.y, 100)

        #undo then redo
        command_stack.undo()
        self.assertEqual(widget.x, 50)
        self.assertEqual(widget.y, 50)
        command_stack.redo()
        self.assertEqual(widget.x, 100)
        self.assertEqual(widget.y, 100)

class TestUndoRedoPasteWidgets(unittest.TestCase):
    def test_undo_redo_paste_widgets(self):
        from AppState import AppState
        from model import ProjectDocument, LabelWidget
        from commands import CommandStack, PasteWidgetsFromClipboard
        from utility import WidgetType

        project_document = ProjectDocument(width=300, height=200, theme={})
        app_state = AppState(project_document)

        widget_1 = LabelWidget(
            id=project_document.id_counters.generate_id(WidgetType.LABEL),
            x=50,
            y=50,
            width=100,
            height=20,
            bg="#111111",
            fg="#aaaaaa",
            text="Paste Widget Test"
        )
        widget_2 = LabelWidget(
            id=project_document.id_counters.generate_id(WidgetType.LABEL),
            x=50,
            y=100,
            width=100,
            height=20,
            bg="#111111",
            fg="#aaaaaa",
            text="Paste Widget Test"
        )
        app_state.add_widget(widget_1)
        app_state.add_widget(widget_2)

        #copy widgets to clipboard
        clipboard = [widget_1.to_dict(), widget_2.to_dict()]

        command_stack = CommandStack()

        #paste widgets from clipboard
        command_stack.execute(
            PasteWidgetsFromClipboard(
                clipboard=clipboard,
                requested_x_offset=50,
                requested_y_offset=50,
                app_state=app_state
            )
        )

        pasted_widget_1 = project_document.widgets[2]
        pasted_widget_2 = project_document.widgets[3]

        self.assertEqual(len(project_document.widgets), 4)          #four widgets in ProjectDocument
        self.assertNotEqual(widget_1.id, pasted_widget_1.id)        #pasted widgets have different IDs
        self.assertNotEqual(widget_2.id, pasted_widget_2.id)
        self.assertEqual(pasted_widget_1.x, 100)                    #pasted widgets are at expected positions
        self.assertEqual(pasted_widget_1.y, 100)
        self.assertEqual(pasted_widget_2.x, 100)
        self.assertEqual(pasted_widget_2.y, 150)
        self.assertEqual(                                           #pasted widgets are selected
            app_state.get_selected_widgets(),
            (pasted_widget_1, pasted_widget_2)
        )
        self.assertEqual(                                           #pasted widget 2 is last selected
            app_state.get_last_selected_widget_id(),
            pasted_widget_2.id
        )

        #undo
        command_stack.undo()
        self.assertEqual(len(project_document.widgets), 2)          #two widgets in ProjectDocument

        #redo
        command_stack.redo()
        redone_widget_1 = project_document.widgets[2]
        redone_widget_2 = project_document.widgets[3]
        self.assertEqual(len(project_document.widgets), 4)          #four widgets in ProjectDocument
        self.assertEqual(redone_widget_1.id, pasted_widget_1.id)    #redone widgets reuse same IDs
        self.assertEqual(redone_widget_2.id, pasted_widget_2.id)

if __name__ == '__main__':
    unittest.main()
