#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QApplication>
#include <QPaintEvent>
#include <QTcpServer>
#include <QList>
#include <QTimer>
#include <QGLWidget>


#include "bike.h"

class MainWindow : public QGLWidget
{
    Q_OBJECT

public:
    MainWindow(QWidget *parent = 0);
    ~MainWindow();
    void reset();

protected:
    void paintEvent(QPaintEvent *e);

private:
    QTcpServer *server;
    QList<Bike *> bikes;
    QTimer *timer;
    int id;
    QTimer *suddenDeathTimer;
    QTimer *timer2;
    bool suddenDeath;

private slots:
    void newConnection();
    void checkClients();
    void chat(QString name, QString message);
    void activateSuddenDeath();
    void clientTimeOut();
};

#endif // MAINWINDOW_H
