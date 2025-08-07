from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.actionbar import ActionBar, ActionView, ActionPrevious, ActionButton
from kivy.properties import ObjectProperty, ListProperty, StringProperty, BooleanProperty
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.config import Config
from kivy.utils import get_color_from_hex
import json
import os

# Configure window for mobile
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Window.size = (360, 640)

# Define matrix colors with updated color scheme
MATRIX_COLORS = {
    'urgent_important': get_color_from_hex('#2ecc71'),  # Green
    'not_urgent_important': get_color_from_hex('#3498db'),  # Blue
    'urgent_not_important': get_color_from_hex('#f1c40f'),  # Yellow
    'not_urgent_not_important': get_color_from_hex('#e74c3c')  # Red
}


# Define custom widget classes
class MatrixButton(Button):
    pass


class TaskItem(BoxLayout):
    checkbox = ObjectProperty(None)
    task_name = ObjectProperty(None)
    index = 0
    open_task = ObjectProperty(None)


class SubtaskItem(BoxLayout):
    checkbox = ObjectProperty(None)
    subtask_name = ObjectProperty(None)
    index = 0
    open_subtask = ObjectProperty(None)


# Load the KV language string
Builder.load_string('''
#:import get_color_from_hex kivy.utils.get_color_from_hex

<MatrixButton>:
    background_color: 
        self.background_color if hasattr(self, 'matrix_id') and self.matrix_id == 'urgent_important' else \
        self.background_color if hasattr(self, 'matrix_id') and self.matrix_id == 'not_urgent_important' else \
        self.background_color if hasattr(self, 'matrix_id') and self.matrix_id == 'urgent_not_important' else \
        self.background_color if hasattr(self, 'matrix_id') and self.matrix_id == 'not_urgent_not_important' else \
        get_color_from_hex('#3498db')
    color: 1, 1, 1, 1
    font_size: '18sp'
    size_hint_y: None
    height: '120dp'
    markup: True
    padding: '10dp'
    halign: 'center'
    valign: 'middle'

<TaskItem>:
    orientation: 'horizontal'
    size_hint_y: None
    height: '60dp'
    checkbox: checkbox
    task_name: task_name
    CheckBox:
        id: checkbox
        size_hint_x: None
        width: '55dp'
        on_touch_down: if self.collide_point(*args[1].pos): args[1].grab(self)
    Button:
        text: ''
        id: task_name
        background_color: (0, 0, 0, 0)
        halign: 'left'
        valign: 'middle'
        font_size: '18sp'
        size_hint_x: 0.9
        text_size: self.width, None
        on_press: root.open_task(root.index)

<SubtaskItem>:
    orientation: 'horizontal'
    size_hint_y: None
    height: '55dp'
    checkbox: checkbox
    subtask_name: subtask_name
    CheckBox:
        id: checkbox
        size_hint_x: None
        width: '50dp'
        on_touch_down: if self.collide_point(*args[1].pos): args[1].grab(self)
    Button:
        text: ''
        id: subtask_name
        background_color: (0, 0, 0, 0)
        halign: 'left'
        valign: 'middle'
        font_size: '16sp'
        size_hint_x: 0.9
        text_size: self.width, None
        on_press: root.open_subtask(root.index)

<MainMenuScreen>:
    BoxLayout:
        orientation: 'vertical'

        ActionBar:
            size_hint_y: 0.1
            ActionView:
                ActionPrevious:
                    title: 'Eisen'
                    with_previous: False
                ActionButton:
                    text: 'Projects'
                    on_press: root.show_projects()

        # Project name display
        Label:
            id: project_name_label
            text: 'No Project Selected'
            size_hint_y: None
            height: '30dp'
            halign: 'center'
            valign: 'middle'
            font_size: '20sp'
            bold: True
            color: 1, 1, 1, 1

        GridLayout:
            id: matrix_grid
            cols: 2
            spacing: '8dp'
            padding: '8dp'
            size_hint_y: 0.7

        Button:
            text: 'Summary'
            size_hint_y: 0.15
            font_size: '16sp'
            on_press: root.show_summary()

<ProjectScreen>:
    BoxLayout:
        orientation: 'vertical'

        ActionBar:
            size_hint_y: 0.1
            ActionView:
                ActionPrevious:
                    title: 'Projects'
                    on_press: root.manager.current = 'main'
                ActionButton:
                    text: 'Add Project'
                    on_press: root.add_project()

        ScrollView:
            BoxLayout:
                id: projects_list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: '10dp'
                padding: '10dp'

<MatrixScreen>:
    BoxLayout:
        orientation: 'vertical'

        ActionBar:
            size_hint_y: 0.1
            ActionView:
                ActionPrevious:
                    title: root.matrix_name
                    on_press: root.manager.current = 'main'
                ActionButton:
                    id: delete_button
                    text: 'X'
                    disabled: True
                    on_press: root.delete_selected()
                ActionButton:
                    id: move_button
                    text: '<->'
                    disabled: True
                    on_press: root.show_move_options()
                ActionButton:
                    text: '+'
                    on_press: root.add_task()

        ScrollView:
            BoxLayout:
                id: tasks_list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: '5dp'
                padding: '5dp'

<TaskScreen>:
    BoxLayout:
        orientation: 'vertical'

        ActionBar:
            size_hint_y: 0.1
            ActionView:
                ActionPrevious:
                    title: root.task_name
                    on_press: root.manager.current = 'matrix'
                ActionButton:
                    id: delete_button
                    text: 'X'
                    disabled: True
                    on_press: root.delete_selected()
                ActionButton:
                    text: 'A->B'
                    on_press: root.edit_task()
                ActionButton:
                    text: '+'
                    on_press: root.add_subtask()

        BoxLayout:
            orientation: 'vertical'
            padding: '10dp'
            spacing: '10dp'
            size_hint_y: 0.3

            Label:
                text: 'Description:'
                size_hint_y: None
                height: '30dp'
                halign: 'left'
                text_size: self.width, None
                font_size: '18sp'

            ScrollView:
                Label:
                    id: task_description
                    text: ''
                    size_hint_y: None
                    height: self.texture_size[1]
                    text_size: self.width, None
                    halign: 'left'
                    valign: 'top'
                    font_size: '16sp'

            Label:
                text: 'Subtasks:'
                size_hint_y: None
                height: '30dp'
                halign: 'left'
                text_size: self.width, None
                font_size: '18sp'

        ScrollView:
            size_hint_y: 0.6
            BoxLayout:
                id: subtasks_list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: '5dp'
                padding: '5dp'

<SummaryScreen>:
    BoxLayout:
        orientation: 'vertical'

        ActionBar:
            id: action_bar
            size_hint_y: 0.1
            ActionView:
                ActionPrevious:
                    id: title_text
                    title: 'Summary'
                    on_press: root.manager.current = 'main'

        ScrollView:
            BoxLayout:
                id: summary_content
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: '10dp'
                padding: '10dp'
''')


class Project:
    def __init__(self, name):
        self.name = name
        self.matrices = {
            'urgent_important': {'name': 'Urgent\nImportant', 'tasks': []},
            'not_urgent_important': {'name': 'Not Urgent\nImportant', 'tasks': []},
            'urgent_not_important': {'name': 'Urgent\nNot Important', 'tasks': []},
            'not_urgent_not_important': {'name': 'Not Urgent\nNot Important', 'tasks': []}
        }

    def to_dict(self):
        return {
            'name': self.name,
            'matrices': self.matrices
        }

    @classmethod
    def from_dict(cls, data):
        project = cls(data['name'])
        project.matrices = data['matrices']
        return project


class Task:
    def __init__(self, name, description=''):
        self.name = name
        self.description = description
        self.subtasks = []

    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'subtasks': self.subtasks
        }

    @classmethod
    def from_dict(cls, data):
        task = cls(data['name'], data['description'])
        task.subtasks = data['subtasks']
        return task


class MainMenuScreen(Screen):
    current_project = ObjectProperty(None)

    def on_enter(self):
        if not self.current_project and App.get_running_app().projects:
            self.current_project = App.get_running_app().projects[0]
        self.update_project_name()
        self.update_matrix_grid()

    def update_project_name(self):
        if self.current_project:
            self.ids.project_name_label.text = self.current_project.name
        else:
            self.ids.project_name_label.text = 'No Project Selected'

    def update_matrix_grid(self):
        grid = self.ids.matrix_grid
        grid.clear_widgets()

        if not self.current_project:
            return

        for matrix_id, matrix_data in self.current_project.matrices.items():
            btn = MatrixButton(text=f'[b]{matrix_data["name"]}[/b]')
            btn.matrix_id = matrix_id
            btn.background_color = MATRIX_COLORS[matrix_id]
            btn.bind(on_press=lambda instance, mid=matrix_id: self.open_matrix(mid))
            grid.add_widget(btn)

    def open_matrix(self, matrix_id):
        matrix_screen = self.manager.get_screen('matrix')
        matrix_screen.current_project = self.current_project
        matrix_screen.matrix_id = matrix_id
        matrix_screen.matrix_name = self.current_project.matrices[matrix_id]['name']
        self.manager.current = 'matrix'

    def show_summary(self):
        summary_screen = self.manager.get_screen('summary')
        summary_screen.current_project = self.current_project
        self.manager.current = 'summary'

    def show_projects(self):
        self.manager.current = 'projects'


class ProjectScreen(Screen):
    def on_enter(self):
        self.update_projects_list()

    def update_projects_list(self):
        projects_list = self.ids.projects_list
        projects_list.clear_widgets()

        app = App.get_running_app()

        for project in app.projects:
            project_box = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp')

            project_btn = Button(text=project.name, size_hint_x=0.6)
            project_btn.bind(on_press=lambda instance, p=project: self.select_project(p))

            rename_btn = Button(text='Rename', size_hint_x=0.2)
            rename_btn.bind(on_press=lambda instance, p=project: self.rename_project(p))

            delete_btn = Button(text='Delete', size_hint_x=0.2)
            delete_btn.bind(on_press=lambda instance, p=project: self.delete_project(p))

            project_box.add_widget(project_btn)
            project_box.add_widget(rename_btn)
            project_box.add_widget(delete_btn)
            projects_list.add_widget(project_box)

    def select_project(self, project):
        main_screen = self.manager.get_screen('main')
        main_screen.current_project = project
        main_screen.update_project_name()
        self.manager.current = 'main'

    def add_project(self):
        popup_content = BoxLayout(orientation='vertical', padding='10dp', spacing='10dp')

        input_field = TextInput(hint_text='Project name', multiline=False, size_hint_y=None, height='40dp')

        buttons_box = BoxLayout(size_hint_y=None, height='50dp')

        cancel_btn = Button(text='Cancel')
        cancel_btn.bind(on_press=lambda instance: popup.dismiss())

        add_btn = Button(text='Add')
        add_btn.bind(on_press=lambda instance: self.create_project(input_field.text, popup))

        buttons_box.add_widget(cancel_btn)
        buttons_box.add_widget(add_btn)

        popup_content.add_widget(input_field)
        popup_content.add_widget(buttons_box)

        popup = Popup(title='Add New Project', content=popup_content, size_hint=(0.8, 0.4))
        popup.open()

    def create_project(self, name, popup):
        if name:
            app = App.get_running_app()
            app.projects.append(Project(name))
            app.save_data()
            self.update_projects_list()
        popup.dismiss()

    def rename_project(self, project):
        popup_content = BoxLayout(orientation='vertical', padding='10dp', spacing='10dp')

        input_field = TextInput(text=project.name, multiline=False, size_hint_y=None, height='40dp')

        buttons_box = BoxLayout(size_hint_y=None, height='50dp')

        cancel_btn = Button(text='Cancel')
        cancel_btn.bind(on_press=lambda instance: popup.dismiss())

        rename_btn = Button(text='Rename')
        rename_btn.bind(on_press=lambda instance: self.update_project_name(project, input_field.text, popup))

        buttons_box.add_widget(cancel_btn)
        buttons_box.add_widget(rename_btn)

        popup_content.add_widget(input_field)
        popup_content.add_widget(buttons_box)

        popup = Popup(title='Rename Project', content=popup_content, size_hint=(0.8, 0.4))
        popup.open()

    def update_project_name(self, project, new_name, popup):
        if new_name:
            project.name = new_name
            App.get_running_app().save_data()
            self.update_projects_list()
        popup.dismiss()

    def delete_project(self, project):
        app = App.get_running_app()
        if project in app.projects:
            app.projects.remove(project)
            if project == self.manager.get_screen('main').current_project:
                self.manager.get_screen('main').current_project = None
                self.manager.get_screen('main').update_project_name()
            app.save_data()
            self.update_projects_list()


class MatrixScreen(Screen):
    current_project = ObjectProperty(None)
    matrix_id = StringProperty('')
    matrix_name = StringProperty('')

    def on_enter(self):
        self.update_tasks_list()
        self.update_action_buttons()

    def update_tasks_list(self):
        tasks_list = self.ids.tasks_list
        tasks_list.clear_widgets()

        if not self.current_project:
            return

        tasks = self.current_project.matrices[self.matrix_id]['tasks']

        for i, task_data in enumerate(tasks):
            taskd = Task.from_dict(task_data)

            task_item = TaskItem()
            task_item.task_name.text = taskd.name
            task_item.index = i
            task_item.checkbox.bind(active=lambda checkbox, value: self.update_action_buttons())
            task_item.open_task = self.open_task_details

            tasks_list.add_widget(task_item)

    def open_task_details(self, index):
        task_data = self.current_project.matrices[self.matrix_id]['tasks'][index]
        taskd = Task.from_dict(task_data)

        task_screen = self.manager.get_screen('task')
        task_screen.current_project = self.current_project
        task_screen.matrix_id = self.matrix_id
        task_screen.task_index = index
        task_screen.task_name = taskd.name
        task_screen.task_description = taskd.description
        task_screen.subtasks = taskd.subtasks
        self.manager.current = 'task'

    def update_action_buttons(self):
        delete_button = self.ids.delete_button
        move_button = self.ids.move_button

        has_selected = any(child.checkbox.active for child in self.ids.tasks_list.children
                           if isinstance(child, TaskItem))

        delete_button.disabled = not has_selected
        move_button.disabled = not has_selected

    def add_task(self):
        popup_content = BoxLayout(orientation='vertical', padding='10dp', spacing='10dp')

        name_input = TextInput(hint_text='Task name', multiline=False, size_hint_y=None, height='40dp')
        desc_input = TextInput(hint_text='Description', multiline=True, size_hint_y=None, height='100dp')

        buttons_box = BoxLayout(size_hint_y=None, height='50dp')

        cancel_btn = Button(text='Cancel')
        cancel_btn.bind(on_press=lambda instance: popup.dismiss())

        add_btn = Button(text='Add')
        add_btn.bind(on_press=lambda instance: self.create_task(name_input.text, desc_input.text, popup))

        buttons_box.add_widget(cancel_btn)
        buttons_box.add_widget(add_btn)

        popup_content.add_widget(name_input)
        popup_content.add_widget(desc_input)
        popup_content.add_widget(buttons_box)

        popup = Popup(title='Add New Task', content=popup_content, size_hint=(0.8, 0.6))
        popup.open()

    def create_task(self, name, description, popup):
        if name:
            task = Task(name, description)
            self.current_project.matrices[self.matrix_id]['tasks'].append(task.to_dict())
            App.get_running_app().save_data()
            self.update_tasks_list()
        popup.dismiss()

    def delete_selected(self):
        tasks_to_delete = []

        for i, child in enumerate(self.ids.tasks_list.children):
            if isinstance(child, TaskItem) and child.checkbox.active:
                tasks_to_delete.append(i)

        # Delete in reverse order to avoid index shifting
        for i in sorted(tasks_to_delete, reverse=True):
            del self.current_project.matrices[self.matrix_id]['tasks'][i]

        App.get_running_app().save_data()
        self.update_tasks_list()
        self.update_action_buttons()

    def show_move_options(self):
        if not self.current_project:
            return

        popup_content = BoxLayout(orientation='vertical', padding='10dp', spacing='10dp')

        for matrix_id, matrix_data in self.current_project.matrices.items():
            if matrix_id != self.matrix_id:
                btn = Button(
                    text=matrix_data['name'],
                    size_hint_y=None,
                    height='50dp',
                    background_color=MATRIX_COLORS[matrix_id],
                    halign='center',
                    valign='middle'
                )
                btn.bind(on_press=lambda instance, mid=matrix_id: self.move_selected(mid, popup))
                popup_content.add_widget(btn)

        cancel_btn = Button(text='Cancel', size_hint_y=None, height='50dp')
        cancel_btn.bind(on_press=lambda instance: popup.dismiss())
        popup_content.add_widget(cancel_btn)

        popup = Popup(title='Move To', content=popup_content, size_hint=(0.8, 0.6))
        popup.open()

    def move_selected(self, target_matrix_id, popup):
        tasks_to_move = []

        for i, child in enumerate(self.ids.tasks_list.children):
            if isinstance(child, TaskItem) and child.checkbox.active:
                tasks_to_move.append(i)

        # Move in reverse order to avoid index shifting
        for i in sorted(tasks_to_move, reverse=True):
            task = self.current_project.matrices[self.matrix_id]['tasks'].pop(i)
            self.current_project.matrices[target_matrix_id]['tasks'].append(task)

        App.get_running_app().save_data()
        self.update_tasks_list()
        self.update_action_buttons()
        popup.dismiss()


class TaskScreen(Screen):
    current_project = ObjectProperty(None)
    matrix_id = StringProperty('')
    task_index = 0
    task_name = StringProperty('')
    task_description = StringProperty('')
    subtasks = ListProperty([])

    def on_enter(self):
        self.ids.task_description.text = self.task_description
        self.update_subtasks_list()
        self.update_action_buttons()

    def update_subtasks_list(self):
        subtasks_list = self.ids.subtasks_list
        subtasks_list.clear_widgets()

        for i, subtask_data in enumerate(self.subtasks):
            subtask_item = SubtaskItem()
            subtask_item.subtask_name.text = subtask_data['name']
            subtask_item.index = i
            subtask_item.checkbox.bind(active=lambda checkbox, value: self.update_action_buttons())
            subtask_item.open_subtask = self.open_subtask_details

            subtasks_list.add_widget(subtask_item)

    def open_subtask_details(self, index):
        self.show_subtask_details(index)

    # In the TaskScreen class, replace the show_subtask_details method with this:

    def show_subtask_details(self, idx):
        subtask = self.subtasks[idx]

        popup_content = BoxLayout(orientation='vertical', padding='10dp', spacing='10dp')

        # Change from a Label to a TextInput for editing the name
        name_input = TextInput(text=subtask['name'], multiline=False, size_hint_y=None, height='40dp')

        desc_label = Label(text="Description:", halign='left', text_size=(None, None), size_hint_y=None, height='30dp')
        desc_input = TextInput(text=subtask['description'], multiline=True, size_hint_y=None, height='150dp')

        buttons_box = BoxLayout(size_hint_y=None, height='50dp')

        close_btn = Button(text='Close')
        close_btn.bind(on_press=lambda instance: popup.dismiss())

        save_btn = Button(text='Save')
        # Update the save function to handle both name and description
        save_btn.bind(on_press=lambda instance: self.update_subtask(idx, name_input.text, desc_input.text, popup))

        buttons_box.add_widget(close_btn)
        buttons_box.add_widget(save_btn)

        popup_content.add_widget(name_input)  # Add the name input field
        popup_content.add_widget(desc_label)
        popup_content.add_widget(desc_input)
        popup_content.add_widget(buttons_box)

        popup = Popup(title='Subtask', content=popup_content, size_hint=(0.8, 0.6))
        popup.open()

    # Replace the update_subtask_description method with this new method:

    def update_subtask(self, idx, new_name, new_description, popup):
        # Update both the name and description
        self.subtasks[idx]['name'] = new_name
        self.subtasks[idx]['description'] = new_description

        # Update the task in the project
        task = self.current_project.matrices[self.matrix_id]['tasks'][self.task_index]
        task['subtasks'] = self.subtasks

        App.get_running_app().save_data()
        # Refresh the subtask list to show the updated name
        self.update_subtasks_list()
        popup.dismiss()

    def update_action_buttons(self):
        delete_button = self.ids.delete_button

        has_selected = any(child.checkbox.active for child in self.ids.subtasks_list.children
                           if isinstance(child, SubtaskItem))

        delete_button.disabled = not has_selected

    def edit_task(self):
        popup_content = BoxLayout(orientation='vertical', padding='10dp', spacing='10dp')

        name_label = Label(text='Task Name:', size_hint_y=None, height='30dp', halign='left')
        name_input = TextInput(text=self.task_name, multiline=False, size_hint_y=None, height='40dp')

        desc_label = Label(text='Description:', size_hint_y=None, height='30dp', halign='left')
        desc_input = TextInput(text=self.task_description, multiline=True, size_hint_y=None, height='100dp')

        buttons_box = BoxLayout(size_hint_y=None, height='50dp')

        cancel_btn = Button(text='Cancel')
        cancel_btn.bind(on_press=lambda instance: popup.dismiss())

        save_btn = Button(text='Save')
        save_btn.bind(on_press=lambda instance: self.update_task(name_input.text, desc_input.text, popup))

        buttons_box.add_widget(cancel_btn)
        buttons_box.add_widget(save_btn)

        popup_content.add_widget(name_label)
        popup_content.add_widget(name_input)
        popup_content.add_widget(desc_label)
        popup_content.add_widget(desc_input)
        popup_content.add_widget(buttons_box)

        popup = Popup(title='Edit Task', content=popup_content, size_hint=(0.8, 0.6))
        popup.open()

    def update_task(self, new_name, new_description, popup):
        if new_name:  # Name is required
            self.task_name = new_name
            self.task_description = new_description

            # Update the task in the project
            task = self.current_project.matrices[self.matrix_id]['tasks'][self.task_index]
            task['name'] = new_name
            task['description'] = new_description

            App.get_running_app().save_data()

            # Update the UI elements
            self.manager.get_screen('task').task_name = new_name
            self.ids.task_description.text = new_description
        popup.dismiss()

    def add_subtask(self):
        popup_content = BoxLayout(orientation='vertical', padding='10dp', spacing='10dp')

        name_input = TextInput(hint_text='Subtask name', multiline=False, size_hint_y=None, height='40dp')
        desc_input = TextInput(hint_text='Description', multiline=True, size_hint_y=None, height='100dp')

        buttons_box = BoxLayout(size_hint_y=None, height='50dp')

        cancel_btn = Button(text='Cancel')
        cancel_btn.bind(on_press=lambda instance: popup.dismiss())

        add_btn = Button(text='Add')
        add_btn.bind(on_press=lambda instance: self.create_subtask(name_input.text, desc_input.text, popup))

        buttons_box.add_widget(cancel_btn)
        buttons_box.add_widget(add_btn)

        popup_content.add_widget(name_input)
        popup_content.add_widget(desc_input)
        popup_content.add_widget(buttons_box)

        popup = Popup(title='Add New Subtask', content=popup_content, size_hint=(0.8, 0.6))
        popup.open()

    def create_subtask(self, name, description, popup):
        if name:
            subtask = {
                'name': name,
                'description': description
            }
            self.subtasks.append(subtask)

            # Update the task in the project
            task = self.current_project.matrices[self.matrix_id]['tasks'][self.task_index]
            task['subtasks'] = self.subtasks

            App.get_running_app().save_data()
            self.update_subtasks_list()
        popup.dismiss()

    def delete_selected(self):
        subtasks_to_delete = []

        for i, child in enumerate(self.ids.subtasks_list.children):
            if isinstance(child, SubtaskItem) and child.checkbox.active:
                subtasks_to_delete.append(i)

        # Delete in reverse order to avoid index shifting
        for i in sorted(subtasks_to_delete, reverse=True):
            del self.subtasks[i]

        # Update the task in the project
        task = self.current_project.matrices[self.matrix_id]['tasks'][self.task_index]
        task['subtasks'] = self.subtasks

        App.get_running_app().save_data()
        self.update_subtasks_list()
        self.update_action_buttons()


class SummaryScreen(Screen):
    current_project = ObjectProperty(None)

    def on_enter(self):
        # Update the title to include project name
        if self.current_project:
            self.ids.action_bar.children[0].children[0].title = f"Summary - {self.current_project.name}"
        else:
            self.ids.action_bar.children[0].children[0].title = "Summary"

        self.update_summary()

    # In the SummaryScreen class, replace the update_summary method with this:

    def update_summary(self):
        summary_content = self.ids.summary_content
        summary_content.clear_widgets()

        if not self.current_project:
            return

        for matrix_id, matrix_data in self.current_project.matrices.items():
            matrix_box = BoxLayout(orientation='vertical', size_hint_y=None, height=0)
            matrix_box.bind(minimum_height=matrix_box.setter('height'))

            matrix_title = Label(
                text=f'[b]{matrix_data["name"]}[/b]',
                size_hint_y=None,
                height='40dp',
                markup=True,
                halign='center',
                text_size=(None, None),
                font_size='16sp',
                color=MATRIX_COLORS[matrix_id]
            )
            matrix_box.add_widget(matrix_title)

            if not matrix_data['tasks']:
                no_tasks_label = Label(
                    text='No tasks',
                    size_hint_y=None,
                    height='30dp',
                    halign='left',
                    text_size=(None, None),
                    font_size='14sp'
                )
                matrix_box.add_widget(no_tasks_label)
            else:
                for task_data in matrix_data['tasks']:
                    task = Task.from_dict(task_data)

                    task_box = BoxLayout(orientation='vertical', size_hint_y=None, height=0)
                    task_box.bind(minimum_height=task_box.setter('height'))

                    task_name = Label(
                        text=f'• {task.name}',
                        size_hint_y=None,
                        height='30dp',
                        halign='left',
                        text_size=(None, None),
                        font_size='14sp'
                    )
                    task_box.add_widget(task_name)

                    # Show subtasks instead of description
                    if task.subtasks:
                        for subtask in task.subtasks:
                            subtask_name = Label(
                                text=f'    - {subtask["name"]}',
                                size_hint_y=None,
                                height='25dp',
                                halign='left',
                                text_size=(None, None),
                                font_size='12sp'
                            )
                            task_box.add_widget(subtask_name)

                    matrix_box.add_widget(task_box)

            summary_content.add_widget(matrix_box)

class EisenApp(App):
    projects = ListProperty([])
    data_file = 'eisen.json'

    def build(self):
        self.load_data()

        sm = ScreenManager()

        sm.add_widget(MainMenuScreen(name='main'))
        sm.add_widget(ProjectScreen(name='projects'))
        sm.add_widget(MatrixScreen(name='matrix'))
        sm.add_widget(TaskScreen(name='task'))
        sm.add_widget(SummaryScreen(name='summary'))

        return sm

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.projects = [Project.from_dict(p) for p in data]
            except Exception as e:
                print(f"Error loading data: {e}")
                self.projects = [Project("Default Project")]
        else:
            self.projects = [Project("Default Project")]
            self.save_data()

    def save_data(self):
        try:
            with open(self.data_file, 'w') as f:
                json.dump([p.to_dict() for p in self.projects], f)
        except Exception as e:
            print(f"Error saving data: {e}")


if __name__ == '__main__':
    EisenApp().run()
