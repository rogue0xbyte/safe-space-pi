from fastapi import FastAPI, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import os
import json

app = FastAPI()

class Session(BaseModel):
    session_no: int
    CO: float
    LEL: float
    H2S: float
    JOB: str
    EQPT: str
    TIME_IN: str
    TIME_OUT: str

class SessionInfo(BaseModel):
    CO: float
    LEL: float
    H2S: float

@app.get("/live_data")
def get_live_data():
    try:
        last_session = 0
        for i in os.listdir("data"):
            if i.startswith("session-"):
                if "history" not in i:
                    session_no = int(i.split("session-")[-1].split(".csv")[0])
                    if last_session<session_no:
                        last_session = session_no
        with open(f"data/session-{last_session}.csv", "r") as f:
            live_data = f.readlines()[-1]
            live_data = live_data.split(", ")
            return {
                "CO": live_data[0],
                "LEL": live_data[1],
                "H2S": live_data[2].strip("\n")
            }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="No live data available.")

@app.put("/update_job_equipment")
def update_job_equipment(JOB: str, EQPT: str):
    try:
        last_eqfile = 0
        for i in os.listdir():
            if i.startswith("job_equipment-"):
                eqfile_no = int(i.split("job_equipment-")[-1].split(".json")[0])
                if last_eqfile<eqfile_no:
                    last_eqfile = eqfile_no
        with open(f"job_equipment-{last_eqfile}.json", "w") as f:
            json.dump({"JOB": JOB, "EQPT": EQPT}, f)
        return {"message": "Job name and equipment number updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update job name and equipment number. {e}")

@app.get("/sessions")
def get_sessions():
    try:
        sessions = []
        with open("data/session-history.csv", "r") as f:
            for line in f.readlines()[1:]:
                session_info = line.split(", ")
                sessions.append(Session(
                    session_no=int(session_info[0]),
                    CO=float(session_info[1]),
                    LEL=float(session_info[2]),
                    H2S=float(session_info[3]),
                    JOB=session_info[4],
                    EQPT=session_info[5],
                    TIME_IN=session_info[6],
                    TIME_OUT=session_info[7].strip()
                ))
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve sessions by job. {e}")

@app.get("/session_by_id/{session_id}")
def get_session_by_id(session_id: int):
    try:
        session_info = []
        with open(f"data/session-{session_id}.csv", "r") as f:
            for line in f.readlines()[1:]:
                i = line.split(", ")
                session_info.append(SessionInfo(
                    CO=float(i[0]),
                    LEL=float(i[1]),
                    H2S=float(i[2]),
                ))
        return session_info
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve session. {e}")

@app.get("/sessions_by_equipment/{equipment_id}")
def get_sessions_by_equipment(equipment_id: str):
    try:
        sessions = []
        with open("data/session-history.csv", "r") as f:
            for line in f.readlines()[1:]:
                session_info = line.split(", ")
                if session_info[5] == equipment_id:
                    sessions.append(Session(
                        session_no=int(session_info[0]),
                        CO=float(session_info[1]),
                        LEL=float(session_info[2]),
                        H2S=float(session_info[3]),
                        JOB=session_info[4],
                        EQPT=session_info[5],
                        TIME_IN=session_info[6],
                        TIME_OUT=session_info[7].strip()
                    ))
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve sessions by equipment. {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)