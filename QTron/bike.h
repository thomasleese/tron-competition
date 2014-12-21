#ifndef BIKE_H
#define BIKE_H

#include <QObject>
#include <QPainter>
#include <QTcpSocket>
#include <QLine>
#include <iostream>
#include <QHostAddress>
#include <QThread>
#include <cmath>
#include <time.h>
#include <stdio.h>

using namespace std;

class Bike : public QObject
{
    Q_OBJECT

public:
    Bike(QTcpSocket *sock, int i);
    void draw(QPainter *painter,QList<Bike *> bikes);
    void run();
    bool hasCollided(QList<Bike *> bikes);
    void setText(QString text);
    void reset();
    void greet();
    bool isReady;
    bool dead;
    bool show;
    bool hadGo;
    int x;
    int y;
    QString name;
    int angle;
    QList<QPoint> linePoints;
    int id;
    bool isDisconnected;
    bool hasHadGo;
    QList<Bike *> bikes;
    QColor colour;
    bool collided;
    float abpool;
    float velocity;
    float speed;
    QTcpSocket *socket;
    bool haveSentAlready;
    bool couldReadLine;

private slots:
    void disconnected();
    void readyRead();

signals:
    void chat(QString name, QString message);
};

#endif // BIKE_H
