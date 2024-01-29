#include <QCoreApplication>
#include <QSerialPort>
#include <QTimer>
#include <QTcpServer>
#include <QTcpSocket>
#include <QDebug>

class SensorReader : public QObject
{
    Q_OBJECT

public:
    explicit SensorReader(QObject *parent = nullptr) : QObject(parent)
    {


        serialPort = new QSerialPort(this);

        // Set the serial port configuration
        serialPort->setPortName("ttyUSB0");  // Change to the appropriate port for your system
        serialPort->setBaudRate(230400);
        serialPort->setDataBits(QSerialPort::Data8);
        serialPort->setParity(QSerialPort::NoParity);
        serialPort->setStopBits(QSerialPort::OneStop);

        // Connect signals and slots
        connect(serialPort, &QSerialPort::readyRead, this, &SensorReader::readSerialData);
        //connect(&timer, &QTimer::timeout, this, &SensorReader::requestData);

        // Start the timer to request data every second
        //timer.start(1000);

        // Open the serial port
        if (serialPort->open(QIODevice::ReadWrite)) {
            qDebug() << "Serial port opened successfully";
        } else {
            qWarning() << "Failed to open serial port:" << serialPort->errorString();
        }

        connect(&tcpServer, &QTcpServer::newConnection, this, &SensorReader::handleNewConnection);
        tcpServer.listen(QHostAddress("192.168.126.237"), 8080);


//        serialPort.setPortName("ttyUSB0");  // Replace with your actual serial port name
//        serialPort.setBaudRate(230400);  // Set your baud rate
//        serialPort.setDataBits(QSerialPort::Data8);
//        serialPort.setParity(QSerialPort::NoParity);
//        serialPort.setStopBits(QSerialPort::OneStop);

//        connect(&serialPort, &QSerialPort::readyRead, this, &SensorReader::readSerialData);

//        connect(&tcpServer, &QTcpServer::newConnection, this, &SensorReader::handleNewConnection);
//        tcpServer.listen(QHostAddress("192.168.126.237"), 8080);  // Set your desired port
//        qDebug() <<"data:" ;
    }

public slots:
    void readSerialData()
    {

        QTcpSocket* client = new QTcpSocket(this);

        QByteArray data = serialPort->readAll();
        QString sensorData = QString::fromUtf8(data);
        qDebug() <<"data:" << data;

        // Send the data over TCP socket to connected clients

            client->connectToHost("192.168.126.237", 8080);
            client->write(sensorData.toUtf8());

    }

    void handleNewConnection()
    {
        QTcpSocket *client = tcpServer.nextPendingConnection();
        clients.append(client);

        connect(client, &QTcpSocket::disconnected, this, &SensorReader::removeClient);
    }

    void removeClient()
    {
        QTcpSocket *client = qobject_cast<QTcpSocket*>(sender());
        if (client)
        {
            clients.removeOne(client);
            client->deleteLater();
        }
    }

private:
    QSerialPort* serialPort;
    QTcpServer tcpServer;
    QList<QTcpSocket*> clients;
};

int main(int argc, char *argv[])
{
    QCoreApplication a(argc, argv);

    SensorReader sensorReader;

    return a.exec();
}

#include "main.moc"





//#include <QCoreApplication>
//#include <QSerialPort>
//#include <QTcpServer>
//#include <QTcpSocket>

//class SensorReader : public QObject
//{
//    Q_OBJECT

//public:
//    explicit SensorReader(QObject *parent = nullptr) : QObject(parent)
//    {


//        serialPort.setPortName("/dev/ttyUSB0");  // Set your serial port name
//        serialPort.setBaudRate(230400);  // Set your baud rate
//        serialPort.setDataBits(QSerialPort::Data8);
//        serialPort.setParity(QSerialPort::NoParity);
//        serialPort.setStopBits(QSerialPort::OneStop);

//        connect(&serialPort, &QSerialPort::readyRead, this, &SensorReader::readSerialData);
//    }

//public slots:
//    void readSerialData()
//    {
//        QByteArray data = serialPort.readAll();
//        // Assuming your sensor data is a string, you might need to parse it accordingly.
//        QString sensorData = QString::fromUtf8(data);

//        // Send the data over TCP socket
//        if (tcpSocket->isOpen())
//        {
//            tcpSocket->write(sensorData.toUtf8());
//        }
//    }

//    void start()
//    {
//        if (serialPort.open(QIODevice::ReadOnly))
//        {
//            qDebug() << "Serial port opened successfully.";

//            // Start TCP server
//            tcpServer.listen(QHostAddress::Any, 8080);  // Set your desired port
//            connect(&tcpServer, &QTcpServer::newConnection, this, &SensorReader::handleNewConnection);
//        }
//        else
//        {
//            qWarning() << "Failed to open serial port!";
//        }
//    }

//    void handleNewConnection()
//    {
//        QTcpSocket* tcpSocket = tcpServer.nextPendingConnection();
//        connect(tcpSocket, &QTcpSocket::disconnected, tcpSocket, &QTcpSocket::deleteLater);
//    }

//private:
//    QSerialPort serialPort;
//    QTcpServer  tcpServer;
//    QTcpSocket* tcpSocket;
//};

//int main(int argc, char *argv[])
//{
//    QCoreApplication a(argc, argv);

//    SensorReader sensorReader;
//    sensorReader.start();

//    return a.exec();
//}

//#include "main.moc"
