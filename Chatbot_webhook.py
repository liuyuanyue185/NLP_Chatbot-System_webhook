from flask import Flask, request
import mysql.connector
from waitress import serve
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

# Create connection
def connect():
    mydb = mysql.connector.connect(
        host='localhost',
        port=3306,
        user='root',
        password='XXX',
        database='testdb',
        connect_timeout = 10000,)
    print(f'I am connecting, testing at {datetime.datetime.now()}')
    return mydb

def autoConnect():
    scheduler=BlockingScheduler()
    scheduler.add_job(connect, 'interval', seconds=7*60*60, id='autoConnectionWithMySQL')
    scheduler.start()


def getText(a):
    if isinstance(a,list):
        return a[0]
    if isinstance(a,dict):
        return a['name']
    return a


app = Flask(__name__)
# check if the web is built correctly
@app.route('/')
def hello_word():
    return 'Hello word everyone'

# test route
@app.route('/test')
def test():
    return 'this is a displaying test'

# test connecting with database
@app.route('/testdatabase')
def testDatabase():
    sql = 'SELECT reply FROM admission_database WHERE program = %s and attribute = %s'
    mycursor.execute(sql, ('computer science', 'transcript',))
    answer = mycursor.fetchall()
    reply = answer[0][0]
    fulfillment = 'the transcript requirement for computer science is: ' + reply
    print(fulfillment)
    return fulfillment

def testRecordFuction():
    sql = 'CREATE TABLE IF NOT EXISTS message_database (name VARCHAR(50), receiver VARCHAR(50), messages VARCHAR(65534), contacts VARCHAR(50))'
    mycursor.execute(sql)
    sqlFormula = 'INSERT INTO message_database (name, receiver, messages, contacts) VALUES (%s, %s, %s, %s)'
    records = [('test', 'test', 'test', 'test'), ]
    mycursor.executemany(sqlFormula, records)
    mydb.commit()

# fetch info based on the request
@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    queryResult = req.get('queryResult')
    action = queryResult.get('action')
    queryResult2 = queryResult.get('outputContexts')
    queryResult3=queryResult2[0]
    program=queryResult3.get('parameters').get('program')
    attribute=queryResult3.get('parameters').get('attribute')
    program=getText(program)
    attribute=getText(attribute)
    fulfillment = ''

    if action == 'getAttribute' or action == 'changeProgram' or action == 'changeAttribute':
        sql = 'SELECT reply FROM admission_database WHERE program = %s and attribute = %s'
        mycursor.execute(sql, (program, attribute,))
        answer = mycursor.fetchall()
        reply = answer[0][0]
        fulfillment = 'the ' + attribute + ' for program of ' + program + ' is: ' + reply
        return {
            'fulfillmentText': fulfillment,
            'source': 'webhookdata'
        }

    if action == 'leaveMessage':
        paras = queryResult3.get('parameters')
        person = paras['name']
        messageReceiver = paras['receiver']
        contact = paras['contact']
        message = queryResult.get('queryText')
        sql = 'CREATE TABLE IF NOT EXISTS message_database (name VARCHAR(50), receiver VARCHAR(50), messages VARCHAR(65534), contacts VARCHAR(50))'
        mycursor.execute(sql)
        sqlFormula = 'INSERT INTO message_database (name, receiver, messages, contacts) VALUES (%s, %s, %s, %s)'
        records = [(person, messageReceiver, message, contact),]
        mycursor.executemany(sqlFormula, records)
        mydb.commit()

    return 'Sorry, the function for related action is not defined'

if __name__ == '__main__':
    mydb=connect()
    mycursor = mydb.cursor()
    mycursor.execute('TRUNCATE admission_database')
    sql = 'CREATE TABLE IF NOT EXISTS admission_database (program VARCHAR(50), attribute VARCHAR(50), reply VARCHAR(65534))'
    mycursor.execute(sql)
    sqlFormula = 'INSERT INTO admission_database (program, attribute, reply) VALUES (%s, %s, %s)'
    records = [('system science', 'all documents',
                'you need to hand up: transcript, English proficiency prove, recommendation letters, resume'),
               ('system science', 'english prove', 'TOEFL 79-80 / IELTS Overall 6.5 - Individual 5.0 (Internet-based)'),
               ('system science', 'transcript',
                '1 transcript is needed, and the other requirement is:Have a bachelor’s degree in Computer Science, Economics, Engineering, Mathematics, Operations Research, Science or a related area with a minimum average of B (70%).'),
               ('system science', 'recommendation letter',
                '2 letters (It is highly recommended that you contact your referee prior to submitting your application to confirm their email address and their availability to complete your letter of recommendation.'),
               ('system science', 'resume', '1 resume is needed'),
               ('system science', 'deadline',
                'for Canadian candidate, it is 1 May for this Fall enrollment while for international students, it is 31 January.'),
               ('system science', 'motivation letter', 'None. No motivation letter is required.'),
               ('computer science', 'all documents',
                'you need to hand up: motivation letter, transcript, English proficiency prove, recommendation letters, resume.'),
               ('computer science', 'english prove',
                'TOEFL 88-89 / IELTS Overall 6.5 - Individual 6.0 (Internet-based)'),
               ('computer science', 'transcript', 'B+ or higher in a related honours bachelor degree'),
               ('computer science', 'recommendation letter',
                '2 (It is highly recommended that you contact your referee prior to submitting your application to confirm their email address and their availability to complete your letter of recommendation.'),
               ('computer science', 'resume', '1 resume is required'),
               ('computer science', 'deadline',
                'for Canadian candidate, it is 1 May for this Fall enrollment while for international students, it is 31 January.'),
               ('computer science', 'motivation letter',
                'Letter of Intent outlining your career goals and proposed research area.'), ]

    mycursor.executemany(sqlFormula, records)
    # mycursor.execute("ALTER TABLE admission_database ADD COLUMN recordID INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY FIRST")
    mydb.commit()
    autoConnect()
    serve(app, host='0.0.0.0', port=8080)


