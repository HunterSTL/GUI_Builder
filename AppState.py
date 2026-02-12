from _dataclasses import ProjectDocument

class AppState:
    """AppState is the central place where all model state changes happen"""
    def __init__(self, project_document: ProjectDocument):
        self.project = project_document

        """
        to be implemented later:
        self.selection = SelectionState (selected ids, last selected...)
        self.mode = DesignerMode (is_dragging, is_selecting...)
        self.history = UndoRedoStack
        self.grid = GridState (visible, color, size)
        """

    #Widgets------------------------------------------------------------------------------------------------------------
    def add_widget(self, model):
        """append a new widget model to the ProjectDocument"""
        self.project.widget_models.append(model)

    def remove_widget(self, model):
        """remove an existing widget model from the ProjectDocument"""
        try:
            self.project.widget_models.remove(model)
        except ValueError:
            pass

    def move_widget_to(self, model, x: int, y: int):
        """set absolute model coordinates"""
        model.x = x
        model.y = y

    def move_widget_by(self, model, dx: int, dy: int):
        """update model coordinates by a delta"""
        model.x += dx
        model.y += dy

    def set_widget_attribute(self, model, attribute, value):
        """set a model attribute to value if present"""
        if hasattr(model, attribute):
            setattr(model, attribute, value)

    #Grid/Project-------------------------------------------------------------------------------------------------------
    def set_grid_visible(self, visible: bool):
        self.project.grid.visible = visible

    def set_grid_size(self, size: int):
        self.project.grid.size = size

    def set_grid_color(self, color: str):
        self.project.grid.color = color

    def set_title(self, title: str):
        self.project.title = title