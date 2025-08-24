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
from kivy.uix.widget import Widget
from kivy.uix.actionbar import ActionBar, ActionView, ActionPrevious, ActionButton
from kivy.properties import ObjectProperty, ListProperty, StringProperty, BooleanProperty
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.config import Config
from kivy.utils import get_color_from_hex, platform
import json
import os

MATRIX_COLORS = {
    'urgent_important': get_color_from_hex('#2ecc71'),
    'not_urgent_important': get_color_from_hex('#3498db'),
    'urgent_not_important': get_color_from_hex('#f1c40f'),
    'not_urgent_not_important': get_color_from_hex('#e74c3c')
}


class MatrixButton(Button):
    pass


class TaskItem(BoxLayout):
    checkbox = ObjectProperty(None)
    task_name = ObjectProperty(None)
    index = 0
    open_task = ObjectProperty(None)

    def on_checkbox_active(self, active):
        if active:
            self.task_name.text = f"[s]{self.task_name.text}[/s]"
        else:
            self.task_name.text = self.task_name.text.replace("[s]", "").replace("[/s]", "")

        app = App.get_running_app()
        matrix_screen = app.root.get_screen('matrix')
        task_data = matrix_screen.current_project.matrices[matrix_screen.matrix_id]['tasks'][self.index]
        task_data['completed'] = active
        app.save_data()


class SubtaskItem(BoxLayout):
    checkbox = ObjectProperty(None)
    subtask_name = ObjectProperty(None)
    index = 0
    open_subtask = ObjectProperty(None)

    def on_checkbox_active(self, active):
        if active:
            self.subtask_name.text = f"[s]{self.subtask_name.text}[/s]"
        else:
            self.subtask_name.text = self.subtask_name.text.replace("[s]", "").replace("[/s]", "")

        app = App.get_running_app()
        task_screen = app.root.get_screen('task')
        subtask = task_screen.subtasks[self.index]
        subtask['completed'] = active

        task = task_screen.current_project.matrices[task_screen.matrix_id]['tasks'][task_screen.task_index]
        task['subtasks'] = task_screen.subtasks
        app.save_data()


Builder.load_string('''
#:import get_color_from_hex kivy.utils.get_color_from_hex
#:import Window kivy.core.window.Window
<MatrixButton>:
    background_color: 
        self.background_color if hasattr(self, 'matrix_id') and self.matrix_id == 'urgent_important' else \
        self.background_color if hasattr(self, 'matrix_id') and self.matrix_id == 'not_urgent_important' else \
        self.background_color if hasattr(self, 'matrix_id') and self.matrix_id == 'urgent_not_important' else \
        self.background_color if hasattr(self, 'matrix_id') and self.matrix_id == 'not_urgent_not_important' else \
        get_color_from_hex('#3498db')
    color: 1, 1, 1, 1
    font_size: Window.height * 0.035 if Window.height < 800 else Window.height * 0.03
    size_hint_y: None
    height: self.parent.height / 2 - self.parent.spacing[1] if self.parent else '120dp'
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
        on_active: root.on_checkbox_active(self.active)
    Button:
        text: ''
        id: task_name
        background_color: (0, 0, 0, 0)
        halign: 'left'
        valign: 'middle'
        font_size: Window.height * 0.03 if Window.height < 800 else Window.height * 0.025
        size_hint_x: 1
        text_size: self.width, None
        markup: True
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
        on_active: root.on_checkbox_active(self.active)
    Button:
        text: ''
        id: subtask_name
        background_color: (0, 0, 0, 0)
        halign: 'left'
        valign: 'middle'
        font_size: Window.height * 0.028 if Window.height < 800 else Window.height * 0.023
        size_hint_x: 1
        text_size: self.width, None
        markup: True
        on_press: root.open_subtask(root.index)
<MainMenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        ActionBar:
            size_hint_y: 0.1
            padding: ['10dp','0dp', '0dp', '0dp']
            ActionView:
                ActionPrevious:
                    app_icon: ''
                    title: 'Eisenhower Matrix'
                    title_font_size: Window.height * 0.075 if Window.height < 800 else Window.height * 0.055
                ActionButton:
                    text: 'Projects'
                    font_size: Window.height * 0.03 if Window.height < 800 else Window.height * 0.025
                    on_press: root.show_projects()
        Label:
            id: project_name_label
            text: 'No Project Selected'
            size_hint_y: None
            height: '30dp'
            halign: 'center'
            valign: 'middle'
            font_size: Window.height * 0.04 if Window.height < 800 else Window.height * 0.035
            bold: True
            color: 1, 1, 1, 1
        GridLayout:
            id: matrix_grid
            cols: 2
            spacing: '8dp'
            padding: '8dp'
            size_hint_y: 0.7
            row_default_height: self.height / 2
        Button:
            text: 'Summary'
            size_hint_y: None
            height: self.parent.height * 0.15
            font_size: Window.height * 0.03 if Window.height < 800 else Window.height * 0.025
            on_press: root.show_summary()
<ProjectScreen>:
    BoxLayout:
        orientation: 'vertical'
        ActionBar:
            size_hint_y: 0.1
            padding: ['10dp','0dp', '0dp', '0dp']
            ActionView:
                ActionPrevious:
                    app_icon: ''
                    title: 'Projects'
                    title_font_size: Window.height * 0.075 if Window.height < 800 else Window.height * 0.055
                    on_press: root.manager.current = 'main'
                ActionButton:
                    text: 'Add Project'
                    font_size: Window.height * 0.03 if Window.height < 800 else Window.height * 0.025
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
            padding: ['10dp','0dp', '0dp', '0dp']
            background_color: root.matrix_color
            background_image: ''
            ActionView:
                ActionPrevious:
                    app_icon: ''
                    title: root.matrix_name
                    title_font_size: Window.height * 0.075 if Window.height < 800 else Window.height * 0.055
                    on_press: root.manager.current = 'main'
                ActionButton:
                    id: delete_button
                    text: 'X'
                    font_size: Window.height * 0.03 if Window.height < 800 else Window.height * 0.025
                    disabled: True
                    on_press: root.delete_selected()
                ActionButton:
                    id: move_button
                    text: '<->'
                    font_size: Window.height * 0.03 if Window.height < 800 else Window.height * 0.025
                    disabled: True
                    on_press: root.show_move_options()
                ActionButton:
                    text: '+'
                    font_size: Window.height * 0.03 if Window.height < 800 else Window.height * 0.025
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
            padding: ['10dp','0dp', '0dp', '0dp']
            ActionView:
                ActionPrevious:
                    app_icon: ''
                    title: root.task_name
                    title_font_size: Window.height * 0.075 if Window.height < 800 else Window.height * 0.055
                    on_press: root.manager.current = 'matrix'
                ActionButton:
                    id: delete_button
                    text: 'X'
                    font_size: Window.height * 0.03 if Window.height < 800 else Window.height * 0.025
                    disabled: True
                    on_press: root.delete_selected()
                ActionButton:
                    text: 'A->B'
                    font_size: Window.height * 0.03 if Window.height < 800 else Window.height * 0.025
                    on_press: root.edit_task()
                ActionButton:
                    text: '+'
                    font_size: Window.height * 0.03 if Window.height < 800 else Window.height * 0.025
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
                font_size: Window.height * 0.03 if Window.height < 800 else Window.height * 0.025
            ScrollView:
                size_hint_y: 1
                Label:
                    id: task_description
                    text: ''
                    size_hint_y: None
                    height: self.texture_size[1]
                    text_size: self.width, None
                    halign: 'left'
                    valign: 'top'
                    font_size: Window.height * 0.028 if Window.height < 800 else Window.height * 0.023
            Label:
                text: 'Subtasks:'
                size_hint_y: None
                height: '30dp'
                halign: 'left'
                text_size: self.width, None
                font_size: Window.height * 0.03 if Window.height < 800 else Window.height * 0.025
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
            padding: ['10dp','0dp', '0dp', '0dp']
            ActionView:
                ActionPrevious:
                    app_icon: ''
                    id: title_text
                    title: 'Summary'
                    title_font_size: Window.height * 0.075 if Window.height < 800 else Window.height * 0.055
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
    def __init__(self, name, description='', completed=False):
        self.name = name
        self.description = description
        self.completed = completed
        self.subtasks = []

    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'completed': self.completed,
            'subtasks': self.subtasks
        }

    @classmethod
    def from_dict(cls, data):
        task = cls(data['name'], data['description'], data.get('completed', False))
        task.subtasks = data['subtasks']
        return task


class MainMenuScreen(Screen):
    current_project = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(MainMenuScreen, self).__init__(**kwargs)
        Clock.schedule_once(self.on_enter)

    def on_enter(self, *args):
        if not self.current_project and App.get_running_app().projects:
            self.current_project = App.get_running_app().projects[0]
        self.update_project_name()
        self.update_matrix_grid()

        Clock.schedule_once(self.force_redraw, 0.1)

    def force_redraw(self, dt):
        Window.update_viewport()

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
            project_btn = Button(text=project.name, size_hint_x=0.7)
            project_btn.bind(on_press=lambda instance, p=project: self.select_project(p))
            rename_btn = Button(text='Rename', size_hint_x=0.2)
            rename_btn.bind(on_press=lambda instance, p=project: self.rename_project(p))
            delete_btn = Button(text='X', size_hint_x=0.1)
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

        top_section = BoxLayout(orientation='vertical', size_hint_y=None, height='60dp')
        input_field = TextInput(hint_text='Project name', multiline=False, size_hint_y=None, height='40dp')
        top_section.add_widget(input_field)

        spacer = Widget(size_hint_y=1)

        buttons_box = BoxLayout(size_hint_y=None, height='50dp')
        cancel_btn = Button(text='Cancel')
        cancel_btn.bind(on_press=lambda instance: popup.dismiss())
        add_btn = Button(text='Add')
        add_btn.bind(on_press=lambda instance: self.create_project(input_field.text, popup))
        buttons_box.add_widget(cancel_btn)
        buttons_box.add_widget(add_btn)

        popup_content.add_widget(top_section)
        popup_content.add_widget(spacer)
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

        top_section = BoxLayout(orientation='vertical', size_hint_y=None, height='60dp')
        input_field = TextInput(text=project.name, multiline=False, size_hint_y=None, height='40dp')
        top_section.add_widget(input_field)

        spacer = Widget(size_hint_y=1)

        buttons_box = BoxLayout(size_hint_y=None, height='50dp')
        cancel_btn = Button(text='Cancel')
        cancel_btn.bind(on_press=lambda instance: popup.dismiss())
        rename_btn = Button(text='Rename')
        rename_btn.bind(on_press=lambda instance: self.update_project_name(project, input_field.text, popup))
        buttons_box.add_widget(cancel_btn)
        buttons_box.add_widget(rename_btn)

        popup_content.add_widget(top_section)
        popup_content.add_widget(spacer)
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

        if len(app.projects) == 1:
            popup_content = BoxLayout(orientation='vertical', padding='10dp', spacing='10dp')
            message = Label(text='Cannot delete the last project', halign='center', valign='middle')
            ok_btn = Button(text='OK', size_hint_y=None, height='50dp')
            ok_btn.bind(on_press=lambda instance: popup.dismiss())

            popup_content.add_widget(message)
            popup_content.add_widget(ok_btn)

            popup = Popup(title='Message', content=popup_content, size_hint=(0.8, 0.3))
            popup.open()
            return

        popup_content = BoxLayout(orientation='vertical', padding='10dp', spacing='10dp')

        top_section = BoxLayout(orientation='vertical', size_hint_y=None, height='80dp')
        message = Label(text=f'Delete "{project.name}" project?',
                        halign='center', valign='middle', markup=True)
        top_section.add_widget(message)

        spacer = Widget(size_hint_y=1)

        buttons_box = BoxLayout(size_hint_y=None, height='50dp')
        cancel_btn = Button(text='Cancel')
        cancel_btn.bind(on_press=lambda instance: popup.dismiss())
        delete_btn = Button(text='Delete')
        delete_btn.bind(on_press=lambda instance: self.confirm_delete_project(project, popup))
        buttons_box.add_widget(cancel_btn)
        buttons_box.add_widget(delete_btn)

        popup_content.add_widget(top_section)
        popup_content.add_widget(spacer)
        popup_content.add_widget(buttons_box)

        popup = Popup(title='Confirm Delete', content=popup_content, size_hint=(0.8, 0.4))
        popup.open()

    def confirm_delete_project(self, project, popup):
        popup.dismiss()  # Close the confirmation popup

        app = App.get_running_app()
        if project in app.projects:
            app.projects.remove(project)

            main_screen = self.manager.get_screen('main')
            if project == main_screen.current_project:
                if app.projects:
                    main_screen.current_project = app.projects[0]
                else:
                    main_screen.current_project = None
                main_screen.update_project_name()

            app.save_data()
            self.update_projects_list()

class MatrixScreen(Screen):
    current_project = ObjectProperty(None)
    matrix_id = StringProperty('')
    matrix_name = StringProperty('')
    matrix_color = ListProperty([0, 0, 0, 1])

    def __init__(self, **kwargs):
        super(MatrixScreen, self).__init__(**kwargs)
        self.bind(matrix_id=self.update_matrix_color)

    def update_matrix_color(self, instance, value):
        if value in MATRIX_COLORS:
            original_color = MATRIX_COLORS[value]
            darkened_color = [
                original_color[0] * 0.3,
                original_color[1] * 0.3,
                original_color[2] * 0.3,
                original_color[3]  # Keep alpha unchanged
            ]
            self.matrix_color = darkened_color

    def on_enter(self):
        self.update_matrix_color(self, self.matrix_id)
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
            if taskd.completed:
                task_item.task_name.text = f"[s]{taskd.name}[/s]"
            else:
                task_item.task_name.text = taskd.name
            task_item.index = i
            task_item.checkbox.active = taskd.completed
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

        top_section = BoxLayout(orientation='vertical', size_hint_y=None, height='160dp')
        name_input = TextInput(hint_text='Task name', multiline=False, size_hint_y=None, height='40dp')
        desc_input = TextInput(hint_text='Description', multiline=True, size_hint_y=None, height='100dp')
        top_section.add_widget(name_input)
        top_section.add_widget(desc_input)

        spacer = Widget(size_hint_y=1)

        buttons_box = BoxLayout(size_hint_y=None, height='50dp')
        cancel_btn = Button(text='Cancel')
        cancel_btn.bind(on_press=lambda instance: popup.dismiss())
        add_btn = Button(text='Add')
        add_btn.bind(on_press=lambda instance: self.create_task(name_input.text, desc_input.text, popup))
        buttons_box.add_widget(cancel_btn)
        buttons_box.add_widget(add_btn)

        popup_content.add_widget(top_section)
        popup_content.add_widget(spacer)
        popup_content.add_widget(buttons_box)
        popup = Popup(title='Add New Task', content=popup_content, size_hint=(0.8, 0.6))
        popup.open()

    def create_task(self, name, description, popup):
        if name:
            task = Task(name, description, False)
            self.current_project.matrices[self.matrix_id]['tasks'].append(task.to_dict())
            App.get_running_app().save_data()
            self.update_tasks_list()
        popup.dismiss()

    def delete_selected(self):
        tasks_to_delete = []
        for child in self.ids.tasks_list.children:
            if isinstance(child, TaskItem) and child.checkbox.active:
                tasks_to_delete.append(child.index)
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
        for child in self.ids.tasks_list.children:
            if isinstance(child, TaskItem) and child.checkbox.active:
                child.checkbox.active = False
                tasks_to_move.append(child.index)
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
            if subtask_data.get('completed', False):
                subtask_item.subtask_name.text = f"[s]{subtask_data['name']}[/s]"
            else:
                subtask_item.subtask_name.text = subtask_data['name']
            subtask_item.index = i
            subtask_item.checkbox.active = subtask_data.get('completed', False)
            subtask_item.checkbox.bind(active=lambda checkbox, value: self.update_action_buttons())
            subtask_item.open_subtask = self.open_subtask_details
            subtasks_list.add_widget(subtask_item)

    def open_subtask_details(self, index):
        self.show_subtask_details(index)

    def show_subtask_details(self, idx):
        subtask = self.subtasks[idx]
        popup_content = BoxLayout(orientation='vertical', padding='10dp', spacing='10dp')

        # Top section with input fields
        top_section = BoxLayout(orientation='vertical', size_hint_y=None, height='240dp')
        name_input = TextInput(text=subtask['name'], multiline=False, size_hint_y=None, height='40dp')
        desc_label = Label(text="Description:", halign='left', text_size=(None, None), size_hint_y=None, height='30dp')
        desc_input = TextInput(text=subtask.get('description', ''), multiline=True, size_hint_y=None, height='150dp')

        top_section.add_widget(name_input)
        top_section.add_widget(desc_label)
        top_section.add_widget(desc_input)

        spacer = Widget(size_hint_y=1)

        buttons_box = BoxLayout(size_hint_y=None, height='50dp')
        close_btn = Button(text='Close')
        close_btn.bind(on_press=lambda instance: popup.dismiss())
        save_btn = Button(text='Save')
        save_btn.bind(on_press=lambda instance: self.update_subtask(idx, name_input.text, desc_input.text, popup))
        buttons_box.add_widget(close_btn)
        buttons_box.add_widget(save_btn)

        popup_content.add_widget(top_section)
        popup_content.add_widget(spacer)
        popup_content.add_widget(buttons_box)
        popup = Popup(title='Subtask', content=popup_content, size_hint=(0.8, 0.6))
        popup.open()

    def update_subtask(self, idx, new_name, new_description, popup):
        self.subtasks[idx]['name'] = new_name
        self.subtasks[idx]['description'] = new_description
        task = self.current_project.matrices[self.matrix_id]['tasks'][self.task_index]
        task['subtasks'] = self.subtasks
        App.get_running_app().save_data()
        self.update_subtasks_list()
        popup.dismiss()

    def update_action_buttons(self):
        delete_button = self.ids.delete_button
        has_selected = any(child.checkbox.active for child in self.ids.subtasks_list.children
                           if isinstance(child, SubtaskItem))
        delete_button.disabled = not has_selected

    def edit_task(self):
        task_data = self.current_project.matrices[self.matrix_id]['tasks'][self.task_index]
        task = Task.from_dict(task_data)
        popup_content = BoxLayout(orientation='vertical', padding='10dp', spacing='10dp')

        top_section = BoxLayout(orientation='vertical', size_hint_y=None, height='200dp')
        name_label = Label(text='Task Name:', size_hint_y=None, height='30dp', halign='left')
        name_input = TextInput(text=self.task_name, multiline=False, size_hint_y=None, height='40dp')
        desc_label = Label(text='Description:', size_hint_y=None, height='30dp', halign='left')
        desc_input = TextInput(text=self.task_description, multiline=True, size_hint_y=None, height='100dp')

        top_section.add_widget(name_label)
        top_section.add_widget(name_input)
        top_section.add_widget(desc_label)
        top_section.add_widget(desc_input)

        spacer = Widget(size_hint_y=1)

        buttons_box = BoxLayout(size_hint_y=None, height='50dp')
        cancel_btn = Button(text='Cancel')
        cancel_btn.bind(on_press=lambda instance: popup.dismiss())
        save_btn = Button(text='Save')
        save_btn.bind(
            on_press=lambda instance: self.update_task(name_input.text, desc_input.text, task.completed, popup))
        buttons_box.add_widget(cancel_btn)
        buttons_box.add_widget(save_btn)

        popup_content.add_widget(top_section)
        popup_content.add_widget(spacer)
        popup_content.add_widget(buttons_box)
        popup = Popup(title='Edit Task', content=popup_content, size_hint=(0.8, 0.6))
        popup.open()

    def update_task(self, new_name, new_description, is_completed, popup):
        if new_name:
            self.task_name = new_name
            self.task_description = new_description
            task = self.current_project.matrices[self.matrix_id]['tasks'][self.task_index]
            task['name'] = new_name
            task['description'] = new_description
            task['completed'] = is_completed
            App.get_running_app().save_data()
            self.manager.get_screen('task').task_name = new_name
            self.ids.task_description.text = new_description
            matrix_screen = self.manager.get_screen('matrix')
            if matrix_screen.current_project == self.current_project and matrix_screen.matrix_id == self.matrix_id:
                matrix_screen.update_tasks_list()
        popup.dismiss()

    def add_subtask(self):
        popup_content = BoxLayout(orientation='vertical', padding='10dp', spacing='10dp')

        # Top section with input fields
        top_section = BoxLayout(orientation='vertical', size_hint_y=None, height='160dp')
        name_input = TextInput(hint_text='Subtask name', multiline=False, size_hint_y=None, height='40dp')
        desc_input = TextInput(hint_text='Description', multiline=True, size_hint_y=None, height='100dp')
        top_section.add_widget(name_input)
        top_section.add_widget(desc_input)

        spacer = Widget(size_hint_y=1)

        buttons_box = BoxLayout(size_hint_y=None, height='50dp')
        cancel_btn = Button(text='Cancel')
        cancel_btn.bind(on_press=lambda instance: popup.dismiss())
        add_btn = Button(text='Add')
        add_btn.bind(on_press=lambda instance: self.create_subtask(name_input.text, desc_input.text, popup))
        buttons_box.add_widget(cancel_btn)
        buttons_box.add_widget(add_btn)

        popup_content.add_widget(top_section)
        popup_content.add_widget(spacer)
        popup_content.add_widget(buttons_box)
        popup = Popup(title='Add New Subtask', content=popup_content, size_hint=(0.8, 0.6))
        popup.open()

    def create_subtask(self, name, description, popup):
        if name:
            subtask = {
                'name': name,
                'description': description,
                'completed': False
            }
            self.subtasks.append(subtask)
            task = self.current_project.matrices[self.matrix_id]['tasks'][self.task_index]
            task['subtasks'] = self.subtasks
            App.get_running_app().save_data()
            self.update_subtasks_list()
        popup.dismiss()

    def delete_selected(self):
        subtasks_to_delete = []
        for child in self.ids.subtasks_list.children:
            if isinstance(child, SubtaskItem) and child.checkbox.active:
                subtasks_to_delete.append(child.index)  # Use the stored index, not the enumeration index
        for i in sorted(subtasks_to_delete, reverse=True):
            del self.subtasks[i]
        task = self.current_project.matrices[self.matrix_id]['tasks'][self.task_index]
        task['subtasks'] = self.subtasks
        App.get_running_app().save_data()
        self.update_subtasks_list()
        self.update_action_buttons()

class SummaryScreen(Screen):
    current_project = ObjectProperty(None)

    def on_enter(self):
        if self.current_project:
            self.ids.action_bar.children[0].children[0].title = f"Summary - {self.current_project.name}"
        else:
            self.ids.action_bar.children[0].children[0].title = "Summary"
        self.update_summary()

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
                        font_size='14sp',
                        markup=True
                    )
                    if task.completed:
                        task_name.text = f'• [s]{task.name}[/s]'
                    task_box.add_widget(task_name)
                    if task.subtasks:
                        for subtask in task.subtasks:
                            subtask_name = Label(
                                text=f'    - {subtask["name"]}',
                                size_hint_y=None,
                                height='25dp',
                                halign='left',
                                text_size=(None, None),
                                font_size='12sp',
                                markup=True
                            )
                            if subtask.get('completed', False):
                                subtask_name.text = f'    - [s]{subtask["name"]}[/s]'
                            task_box.add_widget(subtask_name)
                    matrix_box.add_widget(task_box)
            summary_content.add_widget(matrix_box)


class EisenApp(App):
    projects = ListProperty([])
    data_file = StringProperty('')
    icon = 'logo.png'

    def build(self):
        self.data_file = os.path.join(self.user_data_dir, 'eisen.json')
        self.load_data()
        sm = ScreenManager()
        sm.add_widget(MainMenuScreen(name='main'))
        sm.add_widget(ProjectScreen(name='projects'))
        sm.add_widget(MatrixScreen(name='matrix'))
        sm.add_widget(TaskScreen(name='task'))
        sm.add_widget(SummaryScreen(name='summary'))

        sm.current = 'main'

        if platform == 'android':
            from kivy.core.window import Window
            Window.bind(on_keyboard=self._handle_back_button)

        return sm

    def on_start(self):
        if platform not in ('android', 'ios'):
            Clock.schedule_once(self._set_desktop_window)

    def _set_desktop_window(self, dt):
        Config.set('graphics', 'width', '360')
        Config.set('graphics', 'height', '640')
        Window.size = (360, 640)

    def _handle_back_button(self, window, key, *args):
        if key == 27:  # Back button
            self.root.current = 'main'
            return True
        return False

    def load_data(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.projects = [Project.from_dict(p) for p in data]
            else:
                self.projects = [Project("Default Project")]
                self.save_data()
        except Exception as e:
            print(f"Error loading data: {e}")
            self.projects = [Project("Default Project")]
            try:
                self.save_data()
            except Exception as save_e:
                print(f"Error saving default data: {save_e}")

    def save_data(self):
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, 'w') as f:
                json.dump([p.to_dict() for p in self.projects], f)
        except Exception as e:
            print(f"Error saving data: {e}")


if __name__ == '__main__':
    EisenApp().run()