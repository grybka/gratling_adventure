//This posts an action to the server
//action_id is a uuid4 that the server will use to identify the action
function PostAction(action_id){
    fetch('/action',{
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            action: action_id
        })
    }).then(response => response.json())
    .then(data => {        
        UpdateGameScreen(data);            
        console.log(data);
    });
}         
//This updates the game screen with the new game state
function UpdateGameScreen(game_state){ 
    document.getElementById("room_item").innerHTML = game_state["room_text"];
    document.getElementById("items_item").innerHTML = game_state["items_text"];
    document.getElementById("events_item").innerHTML = game_state["event_text"];
    document.getElementById("status_item").innerHTML = game_state["status_text"];
    //Still to do
    //room image
    //map image
}