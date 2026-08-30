# spinner

This is a loading spinner used during tasks that take a long time, such as when creating scenes, in a game implemented using Python and pandas3D.
It features several small dots that rotate. It is currently in use in  [VoronoiCity3](https://github.com/taKana671/VoronoiCity3.git).

<table>
  <thead>
    <tr>
      <th>normal dots</th>
      <th>shaded dots</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><video src="https://github.com/user-attachments/assets/208aa6e0-55a0-4b80-b45a-912bb4050ac4"></video></td>
      <td><video src="https://github.com/user-attachments/assets/2c41e22f-4c33-43df-965d-50ae1375252b"></video></td> 
    </tr>
  </tbody>  
</table>

# Requirements

* Panda3D 1.10.16
* numpy 2.2.6

# Environment

* Python 3.13
* Windows11

# Usage

For example, if using this loading spinner while creating a scene, create the scene on a thread separate from the main thread, and update the loading spinner on the main thread with each frame update.
Then, once the scene has been created on the separate thread, parent the scene to `base.render` on the main thread.
The following is a code example.

```
from enum import Enum, auto

from direct.stdpy import threading
from direct.showbase.ShowBase import ShowBase
from spinner.spinner_dots import SpinnerDots
...


class Status(Enum):

    ...

    SCENE_CREATE = auto()
    SCENE_WAITING = auto()
    SPINNER_FINISH = auto()
    SCENE_COMPLETE = auto()


class App(ShowBase):

    def __init__(self):
        super().__init__()
        self.disable_mouse

        ...
      
        self.task_mgr.add(self.update, 'update')

     ...

    def update(self, task):
        dt = globalClock.get_dt()

        match self.status:

            ...

            case Status.SCENE_CREATE:
                self.spinner = SpinnerDots(dot_color=(1., 1., 1., .8))
                self.scene_create_thread = threading.Thread(target=scene_create_function)
                self.scene_create_thread.start()
                self.status = Status.SCENE_WAITING

            case Status.SCENE_WAITING:
                self.spinner.update()

                if not self.scene_create_thread.is_alive():
                    self.status = Status.SPINNER_FINISH

            case Status.SPINNER_FINISH:
                if self.spinner.finish():
                    self.spinner.destroy()
                    self.status = Status.SCENE_COMPLETE

            case Status.SCENE_COMPLETE:
                self.scene.reparent_to(self.render)
                self.status = Status.ACTIVE

        # Do somethig else
      
        return task.cont
```

### Parameters

<table>
  <thead>
    <tr>
      <th>parameter</th>
      <th>type</th>
      <th>description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>dot_color</td>
      <td>tuple</td>
      <td>The color of the sprites; (RGBA); specify within the range of 0 to 1.; default is white.</td> 
    </tr>
    <tr>
      <td>dot_cnt</td>
      <td>int</td>
      <td>Number of dots; default is 6.</td>
    </tr>
    <tr>
      <td>shaded</td>
      <td>bool</td>
      <td>If True, shaded circular sprites are created; default is False.</td>
    </tr>
    <tr>
      <td>radius</td>
      <td>float</td>
      <td>The radius of the circle around which the sprites rotate; default is 0.15.</td>
    </tr>
    <tr>
      <td>scale</td>
      <td>float</td>
      <td>The scale of the sprites; default is 0.03.</td>
    </tr>
    <tr>
      <td>duration</td>
      <td>float</td>
      <td>Seconds for a sprite to complete one rotation; default is 3.0 seconds.</td>
    </tr>
  </tbody>  
</table>
