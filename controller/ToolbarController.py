from view import ToolbarView
from events import EventRouter
from utility import Edge

class ToolbarController:
    """Builds the toolbar using the ToolbarView API."""
    def __init__(
        self,
        toolbar_view: ToolbarView,
        event_router: EventRouter
    ) -> None:
        self._toolbar_view: ToolbarView = toolbar_view
        self._event_router: EventRouter = event_router

    def build_toolbar(
        self
    ) -> None:
        """Build the toolbar."""
        self._toolbar_view.create_toolbar()

        self._toolbar_view.add_menu("File")
        self._toolbar_view.add_menu_item(
            menu_name="File",
            label="New",
            command=lambda: self._event_router.emit("project.new"),
            accelerator="[CTRL] + [N]"
        )
        self._toolbar_view.add_menu_item(
            menu_name="File",
            label="Open",
            command=lambda: self._event_router.emit("project.open"),
            accelerator="[CTRL] + [O]"
        )
        self._toolbar_view.add_menu_item(
            menu_name="File",
            label="Save",
            command=lambda: self._event_router.emit("project.save"),
            accelerator="[CTRL] + [S]"
        )
        self._toolbar_view.add_menu_item(
            menu_name="File",
            label="Save as",
            command=lambda: self._event_router.emit("project.save_as"),
            accelerator="[CTRL] + [SHIFT] + [S]"
        )

        self._toolbar_view.add_separator("File")

        self._toolbar_view.add_menu_item(
            menu_name="File",
            label="Exit",
            command=lambda: self._event_router.emit("app.exit"),
            accelerator="[ALT] + [F4]"
        )

        self._toolbar_view.add_menu("Edit")
        self._toolbar_view.add_menu_item(
            menu_name="Edit",
            label="Delete",
            command=lambda: self._event_router.emit("edit.delete"),
            accelerator="[Del]"
        )
        self._toolbar_view.add_menu_item(
            menu_name="Edit",
            label="Copy",
            command=lambda: self._event_router.emit("edit.copy"),
            accelerator="[CTRL] + [C]"
        )
        self._toolbar_view.add_menu_item(
            menu_name="Edit",
            label="Paste",
            command=lambda: self._event_router.emit("edit.paste"),
            accelerator="[CTRL] + [V]"
        )
        self._toolbar_view.add_menu_item(
            menu_name="Edit",
            label="Cut",
            command=lambda: self._event_router.emit("edit.cut"),
            accelerator="[CTRL] + [X]"
        )
        self._toolbar_view.add_menu_item(
            menu_name="Edit",
            label="Undo",
            command=lambda: self._event_router.emit("edit.undo"),
            accelerator="[CTRL] + [Z]"
        )
        self._toolbar_view.add_menu_item(
            menu_name="Edit",
            label="Redo",
            command=lambda: self._event_router.emit("edit.redo"),
            accelerator="[CTRL] + [Y]"
        )

        self._toolbar_view.add_menu("Widgets")
        self._toolbar_view.add_menu_item(
            menu_name="Widgets",
            label="Snap to grid",
            command=lambda: self._event_router.emit("widget.snap_to_grid"),
            accelerator="[S]"
        )
        self._toolbar_view.add_menu_item(
            menu_name="Widgets",
            label="Align left",
            command=lambda: self._event_router.emit("widget.align", edge=Edge.LEFT),
            accelerator="[CTRL] + [←]"
        )
        self._toolbar_view.add_menu_item(
            menu_name="Widgets",
            label="Align right",
            command=lambda: self._event_router.emit("widget.align", edge=Edge.RIGHT),
            accelerator="[CTRL] + [→]"
        )
        self._toolbar_view.add_menu_item(
            menu_name="Widgets",
            label="Align top",
            command=lambda: self._event_router.emit("widget.align", edge=Edge.TOP),
            accelerator="[CTRL] + [↑]"
        )
        self._toolbar_view.add_menu_item(
            menu_name="Widgets",
            label="Align bottom",
            command=lambda: self._event_router.emit("widget.align", edge=Edge.BOTTOM),
            accelerator="[CTRL] + [↓]"
        )
        self._toolbar_view.add_menu_item(
            menu_name="Widgets",
            label="Select all",
            command=lambda: self._event_router.emit("widget.select_all"),
            accelerator="[CTRL] + [A]"
        )

        self._toolbar_view.add_menu("Grid")
        self._toolbar_view.add_checkbox_menu_item(
            menu_name="Grid",
            label="Visualize grid",
            command=lambda: self._event_router.emit("grid.apply_variable"),
            accelerator="[G]",
            variable=self._toolbar_view.grid_visible_variable
        )
        self._toolbar_view.add_menu_item(
            menu_name="Grid",
            label="Change grid size",
            command=lambda: self._event_router.emit("grid.change_size"),
            accelerator="[CTRL] + [G]"
        )
        self._toolbar_view.add_menu_item(
            menu_name="Grid",
            label="Change grid color",
            command=lambda: self._event_router.emit("grid.change_color"),
            accelerator="[SHIFT] + [G]"
        )

        self._toolbar_view.add_menu("Debug")
        self._toolbar_view.add_checkbox_menu_item(
            menu_name="Debug",
            label="Call tracing",
            command=lambda: self._event_router.emit("debug.toggle_call_tracing"),
            accelerator="[CTRL] + [SHIFT] + [T]"
        )
        self._toolbar_view.add_menu_item(
            menu_name="Debug",
            label="Print widget count",
            command=lambda: self._event_router.emit("debug.print_widget_count"),
            accelerator="[#]"
        )
        self._toolbar_view.add_menu_item(
            menu_name="Debug",
            label="Print clipboard",
            command=lambda: self._event_router.emit("debug.print_clipboard"),
            accelerator="[F1]"
        )
        self._toolbar_view.add_menu_item(
            menu_name="Debug",
            label="Print command stack",
            command=lambda: self._event_router.emit("debug.print_command_stack"),
            accelerator="[F2]"
        )
        self._toolbar_view.add_menu_item(
            menu_name="Debug",
            label="Print selection",
            command=lambda: self._event_router.emit("debug.print_selection"),
            accelerator="[F3]"
        )
        self._toolbar_view.add_menu_item(
            menu_name="Debug",
            label="Print bounding boxes",
            command=lambda: self._event_router.emit("debug.print_bounding_boxes"),
            accelerator="[F4]"
        )
        self._toolbar_view.add_menu_item(
            menu_name="Debug",
            label="Print ID counters",
            command=lambda: self._event_router.emit("debug.print_id_counters"),
            accelerator="[F5]"
        )
