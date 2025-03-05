var menu_info={}; //This is a dictionary that holds the menu information for the current room, updated every Posted action
var game_events=[]; //This is a text list of items that have happened
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
        //console.log(data);
    });
}
function ExpandActionMenu(menu_id){
    var menu = document.getElementById("events_item");
    menu.innerHTML += menu_info[menu_id]["text"];
}

function RefreshGame(){
    fetch('/refresh',{
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({})
    }).then(response => response.json())
    .then(data => {        
        UpdateGameScreen(data);            
        console.log(data);
    });
}  
function RegenerateWorld(){
    fetch('/regenerate',{
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({})
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
    console.log(game_events);
    game_events = game_state["events"].concat(game_events);
    var events_html="<ul>";
    game_events.forEach(function (element) {
            events_html+= "<li>"+element+"</li>";
        });
    events_html+="</ul>";
    document.getElementById("events_item").innerHTML = events_html;
    document.getElementById("status_item").innerHTML = game_state["status_text"];
    document.getElementById("game_image").src = game_state["image_name"];
    menu_info = game_state["menu_info"];

    //Still to do
    //map image
}