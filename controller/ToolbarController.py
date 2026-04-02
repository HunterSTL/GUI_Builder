from view import ToolbarView
from EventBus import EventBus

class ToolbarController:
    """
    Builds menu structure using ToolbarView and connects commands to EventBus.
    """
    def __init__(
        self,
        toolbar_view: ToolbarView,
        event_bus: EventBus
    ):
        self.toolbar_view = toolbar_view
        self.event_bus = event_bus

    def build_toolbar(self):
        self.toolbar_view.create_toolbar()

        #file menu
        self.toolbar_view.add_menu("File")
        self.toolbar_view.add_menu_item(
            menu_name="File",
            label="New",
            command=lambda: self.event_bus.emit("project.new"),
            accelerator="[CTRL] + [N]"
        )
        self.toolbar_view.add_menu_item(
            menu_name="File",
            label="Open",
            command=lambda: self.event_bus.emit("project.open"),
            accelerator="[CTRL] + [O]"
        )
        self.toolbar_view.add_menu_item(
            menu_name="File",
            label="Save",
            command=lambda: self.event_bus.emit("project.save"),
            accelerator="[CTRL] + [S]"
        )
        self.toolbar_view.add_menu_item(
            menu_name="File",
            label="Save as",
            command=lambda: self.event_bus.emit("project.save_as"),
            accelerator="[CTRL] + [SHIFT] + [S]"
        )

        self.toolbar_view.add_separator("File")

        self.toolbar_view.add_menu_item(
            menu_name="File",
            label="Exit",
            command=lambda: self.event_bus.emit("app.exit"),
            accelerator="[ALT] + [F4]"
        )

        #edit menu
        self.toolbar_view.add_menu("Edit")
        self.toolbar_view.add_menu_item(
            menu_name="Edit",
            label="Cut",
            command=lambda: self.event_bus.emit("edit.cut"),
            accelerator="[CTRL] + [X]"
        )
        self.toolbar_view.add_menu_item(
            menu_name="Edit",
            label="Copy",
            command=lambda: self.event_bus.emit("edit.copy"),
            accelerator="[CTRL] + [C]"
        )
        self.toolbar_view.add_menu_item(
            menu_name="Edit",
            label="Paste",
            command=lambda: self.event_bus.emit("edit.paste"),
            accelerator="[CTRL] + [V]"
        )
        self.toolbar_view.add_menu_item(
            menu_name="Edit",
            label="Undo",
            command=lambda: self.event_bus.emit("edit.undo"),
            accelerator="[CTRL] + [Z]"
        )
        self.toolbar_view.add_menu_item(
            menu_name="Edit",
            label="Redo",
            command=lambda: self.event_bus.emit("edit.redo"),
            accelerator="[CTRL] + [Y]"
        )

        #widgets menu
        self.toolbar_view.add_menu("Widgets")
        self.toolbar_view.add_menu_item(
            menu_name="Widgets",
            label="Delete",
            command=lambda: self.event_bus.emit("widget.delete"),
            accelerator="[Del]"
        )
        self.toolbar_view.add_menu_item(
            menu_name="Widgets",
            label="Snap to grid",
            command=lambda: self.event_bus.emit("widget.snap_to_grid"),
            accelerator="[S]"
        )
        self.toolbar_view.add_menu_item(
            menu_name="Widgets",
            label="Align left",
            command=lambda: self.event_bus.emit("widget.align.left"),
            accelerator="[CTRL] + [←]"
        )
        self.toolbar_view.add_menu_item(
            menu_name="Widgets",
            label="Align right",
            command=lambda: self.event_bus.emit("widget.align.right"),
            accelerator="[CTRL] + [→]"
        )
        self.toolbar_view.add_menu_item(
            menu_name="Widgets",
            label="Align top",
            command=lambda: self.event_bus.emit("widget.align.top"),
            accelerator="[CTRL] + [↑]"
        )
        self.toolbar_view.add_menu_item(
            menu_name="Widgets",
            label="Align bottom",
            command=lambda: self.event_bus.emit("widget.align.bottom"),
            accelerator="[CTRL] + [↓]"
        )
        self.toolbar_view.add_menu_item(
            menu_name="Widgets",
            label="Select all",
            command=lambda: self.event_bus.emit("widget.select_all"),
            accelerator="[CTRL] + [A]"
        )

        #grid menu
        self.toolbar_view.add_menu("Grid")
        self.toolbar_view.add_checkbox_menu_item(
            menu_name="Grid",
            label="Visualize grid",
            command=lambda: self.event_bus.emit("grid.apply_variable"),
            accelerator="[G]",
            variable=self.toolbar_view.grid_visible_variable
        )
        self.toolbar_view.add_menu_item(
            menu_name="Grid",
            label="Change grid size",
            command=lambda: self.event_bus.emit("grid.change_size"),
            accelerator="[CTRL] + [G]"
        )
        self.toolbar_view.add_menu_item(
            menu_name="Grid",
            label="Change grid color",
            command=lambda: self.event_bus.emit("grid.change_color"),
            accelerator="[SHIFT] + [G]"
        )

        #debug menu
        self.toolbar_view.add_menu("Debug")
        self.toolbar_view.add_checkbox_menu_item(
            menu_name="Debug",
            label="Call tracing",
            command=lambda: self.event_bus.emit("debug.toggle_call_tracing"),
            accelerator="[CTRL] + [SHIFT] + [T]"
        )
        self.toolbar_view.add_menu_item(
            menu_name="Debug",
            label="Set dirty",
            command=lambda: self.event_bus.emit("debug.set_dirty"),
            accelerator="[CTRL] + [D]"
        )
        self.toolbar_view.add_menu_item(
            menu_name="Debug",
            label="Set clean",
            command=lambda: self.event_bus.emit("debug.set_clean"),
            accelerator="[CTRL] + [SHIFT] + [D]"
        )
        self.toolbar_view.add_menu_item(
            menu_name="Debug",
            label="Print widget count",
            command=lambda: self.event_bus.emit("debug.print_widget_count"),
            accelerator="[#]"
        )