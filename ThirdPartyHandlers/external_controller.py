import json
import os

def reconnect_forever(parent, location_of_external_controller):
    while True:
        await asyncio.sleep(10)  
        print("Attempting to connect to external controller...")
        await connect_to_server_and_begin(parent, location_of_external_controller)

async def connect_to_server_and_begin(parent, location_of_external_controller):
    async with websockets.connect(location_of_external_controller) as websocket:
        password_for_controller =  os.environ.get("hoi_exc_s_pw")
        conn_request = {
            "name":"MainServer",
            "password":password_for_controller}
        await websocket.send(json.dumps(conn_request))
        res = await websocket.recv()
        print(f"Response to external controller connection:{}", res)

        if res == "success":
            while True:
                await asyncio.sleep(5) 
                await request_relation_snapshot(parent,websocket)
                await check_and_execute_queue_request(parent,websocket,password_for_controller)

async def request_relation_snapshot(parent, websocket):             
    snapshot_request = {
        "request":"view_relations",
        "password":password_for_controller}
    await websocket.send(json.dumps(snapshot_request))
    snapshot_res = await websocket.recv()
    res_obj = json.loads(response)

    print(f"snapshot response from external controller:{}", snapshot_res)
    if res_obj["status"] == "success":
        parent.external_controller_view_snapshot = snapshot_res

async def check_and_execute_queue_request(parent, websocket,password):
    #service requests on the queue 
    if parent.external_controller_requests.qsize() > 0:
        request = parent.external_controller_requests.get()
        request = json.loads(request)
        request_data = request["data"]
        if request["category"] == "add_relation" or request["category"] == "remove_relation":
            res = add_or_remove_relation(websocket,relation,request["category"],password)
            print(f"add or remove response for relation:{}", res)

async def add_or_remove_relation(websocket,relation,op_code,password):
    request = {"request":op_code,"password":, "relation":relation}
    await websocket.send(json.dumps(request))
    response = await websocket.recv()
    return response