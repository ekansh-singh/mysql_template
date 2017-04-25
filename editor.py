from flask import Flask
from flask import render_template, flash, redirect, request
import MySQLdb
import sys
import unicodedata
import re

app = Flask(__name__)
connection = MySQLdb.connect (host = '34.209.34.113', user = "abcd" , passwd = "abcd", db = "mintshowapp_live")

@app.route('/')
def index():
    cursor = connection.cursor (MySQLdb.cursors.DictCursor)
    query = 'select * from sys_email_templates'
    cursor.execute (query)
    data = cursor.fetchall()
    data_set={}
    for i in data:
        data_set[i['ID']] = {'ID':i['ID'],'Name':i['Name'],'Body':i['Body'],'Desc':i['Desc'],'Subject':i['Subject']}
    return render_template('list_templates.html',data_set=data_set,keys=data_set.keys())


@app.route('/preview-edit/<template_id>', methods=['GET','POST'])
def preview(template_id):
    if request.method=='POST':
        email_template = request.form['ta']
        desc = request.form['desc']
        subject = request.form['subject']
        boundry1 = '<!-- ' + str('#'*121) + '-->'
        boundry2 = '<!-- ' + str('#'*120) + '-->'
        email_template_body = '<bx_include_auto:_email_header.html />'+email_template[email_template.index(boundry1) + len(boundry1):email_template.index(boundry2)]+'<bx_include_auto:_email_footer.html />'
        #print "body in post segment before replacemnet"
        #print email_template_body
        master_list = list(set([line.rstrip('\n') for line in open('master.txt')]))
        for i in master_list:
            if i[1:-1] in email_template_body:
                temp = email_template_body.index(i[1:-1])
                if(not email_template_body[temp-1].isalpha() and not email_template_body[temp+len(i)-2].isalpha()):
                    print i + " Yessssss"
                    email_template_body = email_template_body[:temp] + i + email_template_body[temp+len(i[1:-1]):]

        template_id = int(template_id)
        cursor = connection.cursor ()
        cursor.execute("""
        update sys_email_templates
        set Body=%s
        where ID=%s;
        """,(email_template_body,str(template_id)))
        cursor.execute("""
        update sys_email_templates
        set Subject=%s , 
        `Desc`=%s
        where ID=%s;
        """,(subject,desc,str(template_id)))
        #print "body in post segment after replacement"
        #print email_template_body
        connection.commit()



    # GET request handler

    cursor = connection.cursor (MySQLdb.cursors.DictCursor)
    query = """select * from sys_email_templates where ID="""+str(int(template_id))
    cursor.execute (query)
    data = cursor.fetchall()
    body=''
    description = ''
    subject = ''
    for item in data:
        description = item['Desc']
        subject = item['Subject']
        body = item['Body']
        body = body.replace('<bx_include_auto:_email_header.html/>','')
        body = body.replace('<bx_include_auto:_email_header.html />','')
        body = body.replace('<bx_include_auto:_email_header.html  />','')
        body = body.replace('<bx_include_auto:_email_footer.html />','')
        body = ''.join([i if ord(i) < 128 else ' ' for i in body])
    master_list = [line.rstrip('\n') for line in open('master.txt')]
    #print "body in get before replacement"
    #print body
    for i in master_list:
        body = body.replace(i,i[1:-1])
    #print "body in get after replacement"
    #print body
    header = open('templates/email-header.html','r').read()
    footer = open('templates/email-footer.html','r').read()
    content = header + '<!-- ' + str('#'*121) + '-->' + str(body) + '<!-- '  +str('#'*120) + '-->' + footer
    return render_template('preview-edit.html',subject=subject,content=content,template_id=template_id, description=description)




if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
