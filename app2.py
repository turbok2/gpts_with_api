import requests,os,time

from typing import List
from pydantic import BaseModel, Field
from fastapi import FastAPI, Query,  UploadFile, File, HTTPException
import subprocess
import uuid
from fastapi.responses import FileResponse

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders

def send_email_with_file(subject, body, to_email, attachment_path, attachment_path2):
    # Gmail 계정 설정
    gmail_user = 'turbok2@gmail.com' # 보내는 사람 구글 이메일
    gmail_password = 'wgfa jtbg bsku wnhs'  # 앱 비밀번호

    # 이메일 구성
    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = to_email
    msg['Subject'] = subject

    # 이메일 본문 추가
    msg.attach(MIMEText(body, 'plain'))

    # 첨부파일 추가
    with open(attachment_path, "rb") as attachment:
        part1 = MIMEBase('application', 'octet-stream')
        part1.set_payload(attachment.read())
    encoders.encode_base64(part1)
    part1.add_header(
        "Content-Disposition",
        f"attachment; filename= {attachment_path}",
    )
    msg.attach(part1)
    
    with open(attachment_path2, "rb") as attachment2:
        part2 = MIMEBase('application', 'octet-stream')
        part2.set_payload(attachment2.read())
    encoders.encode_base64(part2)
    part2.add_header(
        "Content-Disposition",
        f"attachment; filename= {attachment_path2}",
    )
    msg.attach(part2)

    # 이메일 서버를 통해 이메일 전송
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(gmail_user, gmail_password)
    text = msg.as_string()
    server.sendmail(gmail_user, to_email, text)
    server.quit()

app = FastAPI(
    title="UML 파일을 읽어 mermaid-cli로 그래프이미지를 만들고 이메일로 보내는 API",
    description="UML 파일을 읽어  mermaid-cli로 그래프를 그리고 이메일로 보내는 API",
    version="0.0.1",
    servers=[
        {
            # "url": "https://b4fe-1-227-21-165.ngrok-free.app",
            # "url": "https://ce2f-1-227-21-165.ngrok-free.app",
            "url": "https://60d4-1-227-21-165.ngrok-free.app",
            "description": "API to read a UML file, draw a graph with mermaid-cli, and email it to someonw",
        }
    ],
)



@app.post("/uml")
async def get_uml(email: str = Query(..., title="email address")):
    """Run mmdc command and send email."""
    # 임시 파일 경로 생성
    temp_input = f"temp1.mmd"
    temp_output = f"{temp_input}.png"

    try:
        # 파일을 임시 경로에 저장
        # with open(temp_input, "wb") as file:
        #     file.write(await mermaid_file.read())

        # mermaid-cli를 사용하여 이미지 생성
        # subprocess.run(["mmdc", "-i", temp_input, "-o", temp_output], check=True)
        result = subprocess.run(["mmdc", "-i", temp_input, "-o", temp_output], capture_output=True, text=True)
        print('result.returncode: ',result.returncode)
        if result.returncode != 0:
            print("Error:", result.stderr)
            raise RuntimeError(f"Mermaid CLI failed: {result.stderr}")        

        # 이미지 파일 반환
        # if not os.path.exists(temp_output):
        #     raise RuntimeError(f"Expected output file at {temp_output} does not exist. Mermaid CLI might have failed.")        
        # print('here : file exist')      
        # file_list = os.listdir('./') 
        # print("file_list : ",file_list)
        # return FileResponse(temp_output, media_type="image")
    except Exception as e:
        print('here : exception')
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # 임시 파일 정리
        print('here : final')
        subject = "UML Diagram"
        body = "UML Diagram"
        to_email =email # "turbok2@gmail.com"
        attachment_path = "temp1.mmd"
        attachment_path2 = "temp1.mmd.png"


        send_email_with_file(subject, body, to_email, attachment_path, attachment_path2)        
        print('send email to ', to_email)
        time.sleep(5)
        subprocess.run(["rm", temp_input, temp_output])
        print('deleted ',temp_input, temp_output)
    return 0


@app.post("/umlfile")
# async def get_uml(mermaid_file: UploadFile = File(...)):
async def get_umlfile(umlcode: str = Query(..., title="uml code")):
    """Save code file."""
    # 임시 파일 경로 생성
    temp_input = f"temp1.mmd"
    # 파일 저장
    a= umlcode.replace('%7B','{').replace('%7D','}').replace('         ','|        ').replace('     ','|    ') #.replace('%20',' ')
    # print('here0')    
    # print(a)
    a= a.split('|')
    # print('here1')    
    # print(a)
    # print('here2')
    with open(temp_input, 'w') as file:
        for i,text in enumerate(a):
            # print(i,text)
            file.writelines(text)
    print('saved ',temp_input)
    return 0