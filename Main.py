from PySide6 import QtCore, QtGui, QtWidgets
from MainView import AppView, Counter
from MainViewModel import ViewModelEventMediator, AppViewModel, CounterModel


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    window.resize(600,100)
    widget = QtWidgets.QWidget()

    mediator = ViewModelEventMediator()

    app_model = AppViewModel('Main', mediator)
    counter_model = CounterModel('Counter', mediator)
    counter_model2 = CounterModel('Counter2', mediator)

    AppView = AppView('Main', app_model)
    counterView = Counter('Counter', counter_model)
    counterView2 = Counter('Counter2', counter_model2)

    AppView.setupUI(widget)
    AppView.addPluginView(counterView)
    AppView.addPluginView(counterView2)

    AppView.run()

    app_model.render()

    window.setCentralWidget(widget)
    window.show()

    sys.exit(app.exec())