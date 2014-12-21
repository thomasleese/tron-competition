#include "mainwindow.h"

MainWindow::MainWindow(QWidget *parent) :
	QGLWidget(parent)
{
    this->setFixedSize(800, 600);
    server = new QTcpServer(this);
    connect(server, SIGNAL(newConnection()), this, SLOT(newConnection()));
    server->listen(QHostAddress::Any, 4567);

    timer = new QTimer(this);
    connect(timer, SIGNAL(timeout()), this, SLOT(update()));
    timer->start(50);

    timer2 = new QTimer(this);
    connect(timer2, SIGNAL(timeout()),this,SLOT(clientTimeOut()));
    timer2->setSingleShot(true);

    suddenDeath = false;
    suddenDeathTimer = new QTimer(this);
    connect(suddenDeathTimer, SIGNAL(timeout()), this, SLOT(activateSuddenDeath()));
    suddenDeathTimer->start(300000);



    id = 0;
}


void MainWindow::clientTimeOut()
{
    cout << "Timeout function called\n";
    Bike *bike;
    foreach(bike,bikes)
    {
        if(!bike->hasHadGo)
        {
            bike->socket->disconnectFromHost();
            bike->dead = true;
            bike->hasHadGo = true;
        }
    }
}

MainWindow::~MainWindow()
{
    delete server;
}

void MainWindow::reset()
{
    suddenDeathTimer->stop();
    suddenDeathTimer->start(300000);
    suddenDeath = false;

    for (int i = 0; i < bikes.count(); i++)
    {
        bikes[i]->reset();
    }
}

void MainWindow::paintEvent(QPaintEvent *e)
{
    if (suddenDeath)
    {
        for (int i = 0; i < bikes.count(); i++)
        {
            bikes[i]->speed *= 1.01;
        }
    }

    e->accept();
    QPainter painter(this);

    painter.fillRect(0, 0, 800, 600, Qt::white);

    bool ready = true;
    for (int i = 0; i < bikes.count(); i++)
    {
        if (!bikes[i]->isReady)
        {
            ready = false;
        }
        bikes[i]->hasHadGo = false;
        bikes[i]->haveSentAlready = false;
    }

    if (ready)
    {
//	cout << ":: Sent move request..." << endl;
        bool alldone = false;
        time_t start = time(NULL);
        while(!alldone){
            for (int i = 0; i < bikes.count(); i++)
            {
                if (bikes[i]->show && !bikes[i]->hasHadGo)
                {
                    bikes[i]->bikes = bikes;
                    bikes[i]->run();
                }
            }
            alldone = true;
            for (int i = 0; i < bikes.count(); i++){
                if(bikes[i]->show && !bikes[i]->hasHadGo){
                    alldone = false;
                }
            }
            if(time(NULL) - 10 > start)
                clientTimeOut();
        }
    }

    if(ready)
    {
        for (int i = 0; i < bikes.count(); i++)
        {
            if (bikes[i]->show)
            {
                bikes[i]->draw(&painter,bikes);
            }
        }
    }

    checkClients();
}

void MainWindow::newConnection()
{
    while (server->hasPendingConnections())
    {
        QTcpSocket *socket = server->nextPendingConnection();
        Bike *bike = new Bike(socket, id);
        connect(bike, SIGNAL(chat(QString,QString)), this, SLOT(chat(QString,QString)));
        id += 1;
        cout << "Resetting from here\n";
        reset();

        bikes.append(bike);
        cout << ":: New Bike: " << socket->peerAddress().toString().toStdString() << endl;
    }
}

void MainWindow::checkClients()
{
    bool everyoneDied = true;

    for (int i = bikes.count() - 1; i >= 0; i--)
    {
        if (bikes[i]->isDisconnected)
        {
            for (int j = 0; j < bikes.count(); j++)
            {
                bikes[j]->setText(QString("DISCO ") + bikes[i]->name + QString("\n"));
            }

            delete bikes[i];
            bikes.removeAt(i);
            cout << ":: Removed Bike: " << i << endl;
        }
        else
        {
            if (!bikes[i]->collided)
            {
                everyoneDied = false;
            }
//            else if (bikes[i]->dead)
//            {
//                everyoneDied = false;
//            }
        }
    }

    if (everyoneDied)
    {
        cout << "resetting from other place\n";
        reset();
    }
}

void MainWindow::chat(QString name, QString message)
{
    QString packet = "CHAT ";
    packet.append(name);
    packet.append(" ");
    packet.append(message);
    packet.append("\n");

    for (int i = 0; i < bikes.count(); i++)
    {
        bikes[i]->setText(packet);
    }
}

void MainWindow::activateSuddenDeath()
{
    if (!suddenDeath)
    {
        suddenDeath = true;
        cout << "SUDDEN DEATH ACTIVATED!" << endl;
        chat("Server", "SUDDEN DEATH ACTIVATED!");
    }
}
