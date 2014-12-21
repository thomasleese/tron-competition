#include "bike.h"

Bike::Bike(QTcpSocket *sock, int i)
{
    socket = sock;
    id = i;

    connect(socket, SIGNAL(readyRead()), this, SLOT(readyRead()));
    connect(socket, SIGNAL(disconnected()), this, SLOT(disconnected()));

    isDisconnected = false;

    x = rand() % 80000;
    y = rand() % 60000;
    //linePoints.append(QPoint(x, y));

    velocity = 100;
    angle = (rand() % 4) * 90;
    abpool = 0;
    name = "";
    show = false;
    isReady = false;
    hadGo = false;
    dead = false;
    collided = false;
    speed = 500;

    colour.setBlue(0);
    colour.setRed(0);
    colour.setGreen(0);

    greet();

    if (!socket->waitForReadyRead(2000))
    {
        socket->disconnectFromHost();
        show = false;
        isReady = true;
        hadGo = false;
    }
}

void Bike::draw(QPainter *painter, QList<Bike *> bikes)
{
    if (show)
    {
        painter->setPen(colour);
        painter->setFont(QFont("sans", 12));

        for (int i = 0; i < linePoints.count(); i++)
        {
            QPoint point1;
            QPoint point2;
            if (i == 0)
            {
                point1 = linePoints[0];
            }
            else
            {
                point1 = linePoints[i - 1];
            }

            point2 = linePoints[i];

            painter->drawLine(point1/100., point2/100.);
        }

        if (!collided)
        {
            collided = hasCollided(bikes);
            if (angle == 0)
            {
                y -= velocity;
            }
            else if (angle == 90)
            {
                x += velocity;
            }
            else if (angle == 180)
            {
                y += velocity;
            }
            else if (angle == 270)
            {
                x -= velocity;
            }
            if (angle == 0 || angle == 180)
            {
                painter->fillRect(x/100. - 5, y/100. - 15, 10, 30, colour);
            }
            else
            {
                painter->fillRect(x/100. - 15, y/100. - 5, 30, 10, colour);
            }
            painter->drawText(x/100., y/100. - 20, name);
        }
        else
        {
            linePoints.clear();
        }




    }
}

void Bike::run()
{
    if(!haveSentAlready){
        for (int i = 0; i < bikes.count(); i++)
        {


            Bike *bike = bikes[i];
            if (bike->isReady && bike->show)
            {
                if (bike->collided)
                {
                    socket->write("DEAD ");
                    socket->write(bike->name.toAscii());
                    socket->write("\n");
                }
                else
                {
                    socket->write("BIKE ");
                    socket->write(bike->name.toAscii());
                    socket->write(" ");
                    socket->write(QString::number(bike->x).toAscii());
                    socket->write(" ");
                    socket->write(QString::number(bike->y).toAscii());
                    socket->write(" ");
                    socket->write(QString::number(bike->colour.red()).toAscii());
                    socket->write(" ");
                    socket->write(QString::number(bike->colour.green()).toAscii());
                    socket->write(" ");
                    socket->write(QString::number(bike->colour.blue()).toAscii());
                    socket->write("\n");
                }
            }
        }
        linePoints.append(QPoint(x, y));
    }



    if (dead)
    {
        show = false;
        isReady = true;
        hadGo = false;
        dead = false;
    }

    if (!dead)
    {
        if(!haveSentAlready){
            socket->write("G\n");
            socket->flush();
        }

        hadGo = false;
        couldReadLine = false;
        if (!socket->waitForReadyRead(1))
        {
            //            socket->disconnectFromHost();
            //            dead = true;
            haveSentAlready = true;
            return;
        }
        if (!hadGo && couldReadLine)
        {
            cout << "KILLING BECAUSE HE DIDN'T HAVE A GO\n";
            socket->disconnectFromHost();
            dead = true;
        }
    }
    if(hadGo || dead)
        hasHadGo = true;

    time_t result = time(NULL);
    cout << result << ": Recieved next move from " << name.toStdString().c_str() << endl;
}

int sign(int x){
    if(x > 0){
        return 1;
    }
    if(x < 0){
        return -1;
    }
    return 0;
}

bool Bike::hasCollided(QList<Bike *> bikes)
{
    // Do collision detection here
    // use linePoints
    int i = linePoints.count() - 1;
    if(i <= 0)
        return false;
    if(linePoints[i-1].x() < 0 || linePoints[i-1].x() >= 80000 || linePoints[i-1].y() < 0 || linePoints[i-1].y() >= 60000)
        return true;
    if(linePoints[i].x() < 0 || linePoints[i].x() >= 80000 || linePoints[i].y() < 0 || linePoints[i].y() >= 60000)
        return true;
    int j, r;
    Bike *bike;
    for(r = 0; r < bikes.count(); r++)
    {
        bike = bikes[r];
        int forsubtract = 1;
        if(bike->name == name){
            forsubtract = 3;
        }
        for(j = 0; j < bike->linePoints.count() - forsubtract; j++)
        {
            int jx = bike->linePoints[j].x();
            int j1x = bike->linePoints[j+1].x();
            int jy = bike->linePoints[j].y();
            int j1y = bike->linePoints[j+1].y();
            int ix = linePoints[i-1].x();
            int i1x = linePoints[i].x();
            int iy = linePoints[i-1].y();
            int i1y = linePoints[i].y();

            if(angle == 0){
                iy += 1;
                i1y -= 1;
            }
            if(angle == 90){
                ix -= 1;
                i1x += 1;
            }
            if(angle == 180){
                iy -= 1;
                i1y += 1;
            }
            if(angle == 270){
                ix += 1;
                i1x -= 1;
            }
            if(!(jx == j1x && i1x == ix) && !(jy == j1y && i1y == iy))
            {

                // If not parallel
                if(jx == j1x)
                {
                    // x equal

                    if((ix > jx && i1x < jx) || (ix < jx && i1x > jx))
                    {
                        if((sign(iy - jy) != sign(iy - j1y)))
                            return true;
                    }
                }
                if(jy == j1y)
                {

                    if((iy > jy && i1y < jy) || (iy < jy && i1y > jy))
                    {
                        if((sign(ix - jx) != sign(ix - j1x)))
                            return true;
                    }
                }
            }
        }
    }
    return false;
}

void Bike::setText(QString text)
{
    socket->write(text.toAscii().data());
    socket->flush();
}

void Bike::reset()
{
    cout << "Reset was called\n";
    x = rand() % 80000;
    y = rand() % 60000;
    cout << "x: " << x << " y: " << y << endl;
    linePoints.clear();

    //linePoints.append(QPoint(x, y));

    velocity = 100;
    angle = 0;
    abpool = 0;
    show = true;
    isReady = true;
    hadGo = false;
    dead = false;
    collided = false;
    speed = 500;

    socket->write("RESET\n");
}

void Bike::greet()
{
    cout << "Greeting\n";
    socket->write("ARENA 80000 60000\n");
}

void Bike::readyRead()
{
    while (socket->canReadLine())
    {
        QByteArray data = socket->readLine();
        QString line = data.trimmed();
        couldReadLine = true;

        if (line == "L")
        {
            angle -= 90;

            if (angle >= 360)
            {
                angle -= 360;
            }
            if (angle < 0)
            {
                angle += 360;
            }
            if(velocity < speed)
                velocity += 30;
            else if(velocity > speed)
                velocity -= 30;
            if(abs(speed-velocity)<30)
                velocity = speed;
            if(abpool<10)
                abpool += 0.2;
            hadGo = true;
        }
        else if (line == "R")
        {
            angle += 90;

            if (angle >= 360)
            {
                angle -= 360;
            }
            if (angle < 0)
            {
                angle += 360;
            }
            if(velocity < speed)
                velocity += 30;
            else if(velocity > speed)
                velocity -= 30;
            if(abs(speed-velocity)<30)
                velocity = speed;
            if(abpool<10)
                abpool += 0.2;
            hadGo = true;
        }
        else if (line == "A")
        {
            if(abpool > 0){
                velocity += 20;
                abpool -= 0.5;
            } else {
                if(velocity < speed)
                    velocity += 30;
                else if(velocity > speed)
                    velocity -= 30;
                if(abs(speed-velocity)<30)
                    velocity = speed;
            }
            hadGo = true;
        }
        else if (line == "D")
        {
            if(abpool > 0){
                velocity -= 20;
                abpool -= 0.5;
            }
            else {
                if(velocity < speed)
                    velocity += 30;
                else if(velocity > speed)
                    velocity -= 30;
                if(abs(speed-velocity)<30)
                    velocity = speed;
            }
            hadGo = true;
        }
        else if (line == "N")
        {

            if(velocity < speed)
                velocity += 30;
            else if(velocity > speed)
                velocity -= 30;
            if(abs(speed-velocity)<30)
                velocity = speed;
            if(abpool<10)
                abpool += 0.2;
            hadGo = true;
        }
        else if (line.startsWith("NAME "))
        {
            name = line.remove(0, 5);
            isReady = true;
            show = true;
        }
        else if (line.startsWith("COLOUR "))
        {
            QStringList list = line.split(" ");
            if (list.count() >= 2)
            {
                colour.setRed(list[1].toInt());
            }
            if (list.count() >= 3)
            {
                colour.setGreen(list[2].toInt());
            }
            if (list.count() >= 4)
            {
                colour.setBlue(list[3].toInt());
            }
        }
        else if (line.startsWith("CHAT "))
        {
            QString message = line.remove(0, 5);

            if (!message.isEmpty())
            {
                emit chat(name, message);
            }

            if(velocity < speed)
                velocity += 30;
            else if(velocity > speed)
                velocity -= 30;
            if(abs(speed-velocity)<30)
                velocity = speed;
            if(abpool<10)
                abpool += 0.2;

            hadGo = true;
        }
    }
}

void Bike::disconnected()
{
    dead = true;
    isDisconnected = true;
    cout << ":: Disconnected: " << socket->peerAddress().toString().toStdString() << endl;
}
