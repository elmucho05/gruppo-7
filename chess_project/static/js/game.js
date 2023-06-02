// window.location.host = www.example.com:8082
const socket = new WebSocket(`ws://${window.location.host}/ws/room/${roomName}`);
const board = Chessboard('board', {
  draggable: true,
  onDragStart: onDragStart,
  onDrop: onDrop,
  onMouseoutSquare: onMouseoutSquare,
  onMouseoverSquare: onMouseoverSquare
});
const chess = new Chess();

var gameStatus = 1; 
var playerOrientation = String();
var playerTimerSeconds = 5*60; // default 5 minutes
var playerTurn = false;
var timerID = null;



/* ----- WebSocket events ----- */
/* ---------------------------- */
function onGameStatusChange(){
  switch (gameStatus) {
    // WAITING_FOR_PLAYER
    case 1: 
      document.querySelector('#game-status').textContent = 'Stato della partita: WAITING_FOR_PLAYER';
      document.getElementById('quit-game').hidden = true;
      document.getElementById('quit-room').hidden = false;
      break;

    // GAME_READY
    case 2: 
      document.querySelector('#game-status').textContent = 'Stato della partita: GAME_READY';
      document.getElementById('quit-game').hidden = false;
      document.getElementById('quit-room').hidden = true;
      break;

    // GAME_END
    case 3: 
      document.querySelector('#game-status').textContent = 'Stato della partita: GAME_END';
      document.querySelector('#player-turn').textContent = "";
      document.getElementById('quit-game').hidden = true;
      document.getElementById('quit-room').hidden = false;
      clearInterval(timerID);
      break;
  
    default:
      break;
  }
}
function onStartGame(data){
  playerOrientation = data['start-game']['player-orientation'][username];
  playerTimerSeconds= data['start-game']['player-timer'][username];
  playerTurn        = data['start-game']['player-turn'][username];
  const fen         = data['start-game']['fen'];

  var playerList = [ ]
  for (const [username, _] of Object.entries(data['start-game']['player-orientation']))
    playerList.push(username);
  
  document.querySelector('#player-list').textContent = `${playerList[0]} vs ${playerList[1]}`;

  displayTime();

  if(playerTurn){
    document.querySelector('#player-turn').textContent = "E' il tuo turno!";
    startTimer();
  }
  else{
    document.querySelector('#player-turn').textContent = "Attendere la mossa dell'avversario";
    clearInterval(timerID);
  }

  board.orientation(playerOrientation);
  board.position(fen);
  chess.load(fen);

}
function onSwapTurns(playerTurns){
  playerTurn = playerTurns[username];
  if(playerTurn){
    document.querySelector('#player-turn').textContent = "E' il tuo turno!";
    startTimer();
  }
  else{
    document.querySelector('#player-turn').textContent = "Attendere la mossa dell'avversario";
    clearInterval(timerID);
  }
}
function onUpdateFen(newFen){
  board.position(newFen);
  chess.load(newFen);
}

function addMoveText(move){
  //const color = move['color'] == 'b' ? 'BLACK':'WHITE';
  const from  = move['from'];
  const to    = move['to'];
  const piece = move['piece']
  const img   = `<img src="${staticUrl}img/chesspieces/wikipedia/${piece}.png" style="width:20px;height:20px;"></img>`
  document.querySelector('#history-moves').innerHTML += `<p style="color:black">${img} : ${from} -> ${to}<\p>`;
}

function onPlayerLeft(player){
  if(player !== username)
    document.querySelector('#player-result').textContent = `Hai vinto! Il giocatore ${player} ha abbandonato la partita`;
}
function onPlayerTimeout(player){
  if(player === username)
    document.querySelector('#player-result').textContent = `Hai perso! Tempo scaduto`;  
  else
    document.querySelector('#player-result').textContent = `Hai vinto! Il giocatore ${player} ha fatto timeout`;
}
function onPlayerCheckmate(winner){
  if(winner === username)
    document.querySelector('#player-result').textContent = `Hai vinto! Hai fatto scacco matto`;  
  else
    document.querySelector('#player-result').textContent = `Hai perso! ${winner} ha fatto scacco matto`;  
}

socket.onclose = function(e){
  alert("Connessione chiusa!");
}
socket.onmessage = function(e){
  const data = JSON.parse(e.data);

  // display chat messages
  if(data.hasOwnProperty('chat-message-text')){
    const from = data['chat-message-from'];
    const text = data['chat-message-text'];
    document.querySelector('#chat-log').value += `[${from}] ${text}\n`;
  }

  // display generic message
  if(data.hasOwnProperty('message')){
    const message = data['message'];
    alert(message);
  }

  // on start game event
  if(data.hasOwnProperty('start-game')){
    onStartGame(data);
  }

  // in game events
  if(data.hasOwnProperty('in-game')){
    // swap turns
    const turns = data['in-game']['swap-turn'];
    onSwapTurns(turns);

    // update chess board fen
    const fen = data['in-game']['new-fen'];
    onUpdateFen(fen);
    
    // append player move in move box
    const move = data['in-game']['move'];
    addMoveText(move);
  }

  // end game event
  if(data.hasOwnProperty('end-game')){
    const reason = data['end-game']['reason'];
    
    // on checkmate
    if(reason === 'checkmate'){
      const winner = data['end-game']['winner'];
      onPlayerCheckmate(winner);
    }

    // on player timeout
    else if(reason === 'player-timeout'){
      const player = data['end-game']['player'];
      onPlayerTimeout(player);
    }

    // on player left
    else if(reason === 'player-left'){
      const player = data['end-game']['player'];
      onPlayerLeft(player);
    }
  }

  // on game status change
  if(data.hasOwnProperty('game-status-code')){
    gameStatus = data['game-status-code']
    onGameStatusChange();
  }
}



/* --------- Board events ---------- */
/* --------------------------------- */
const whiteSquareGrey = '#a9a9a9';
const blackSquareGrey = '#696969';
function removeGreySquares () {
  $('#board .square-55d63').css('background', '')
}

function greySquare (square) {
  var $square = $('#board .square-' + square)

  var background = whiteSquareGrey
  if ($square.hasClass('black-3c85d')) {
    background = blackSquareGrey
  }

  $square.css('background', background)
}

function onDragStart(source, piece, position, orientation) {
  if (socket.readyState !==  WebSocket.OPEN) 
    return false;

  if(gameStatus != 2) // gameStatus != GAME_READY
    return false;

  if(!playerTurn)
    return false;

  if (chess.game_over()) 
    return false

  if ((chess.turn() === 'w' && piece.search(/^b/) !== -1) || (chess.turn() === 'b' && piece.search(/^w/) !== -1)) 
    return false
}

function onDrop(source, target, piece, newPos, oldPos, orientation) {
  removeGreySquares()

  // see if the move is legal
  var move = chess.move({
    from: source,
    to: target,
    piece: piece,
    promotion: 'q' // NOTE: always promote to a queen for example simplicity
  })

  // illegal move
  if (move === null) 
    return 'snapback'

  socket.send(JSON.stringify({
    'new-fen': chess.fen(),
    'move': {
      'from'  : source,
      'to'    : target,
      'piece' : piece
    }
  }));


  if(chess.in_checkmate())
  {
    socket.send(JSON.stringify({
      'checkmate' : true
    }))
  }
    
  
  // if(chess.isDraw())
  //   alert('PAREGGIO');
  
  // if(chess.isStalemate())
  //   alert('STALLO!');

  // if(chess.isGameOver())
  //   alert('GAME OVER!'); 

}

function onMouseoverSquare(square, piece) {
  if(!playerTurn) 
    return;
  
  // get list of possible moves for this square
  var moves = chess.moves({
    square: square,
    verbose: true
  })

  // exit if there are no moves available for this square
  if (moves.length === 0) 
    return

  // highlight the square they moused over
  greySquare(square)

  // highlight the possible squares for this piece
  for (var i = 0; i < moves.length; i++) {
    greySquare(moves[i].to)
  }
}

function onMouseoutSquare (square, piece) {
  removeGreySquares()
}



/* ----- Timer Function  ----- */
/* --------------------------- */
function startTimer(){
  timerID = setInterval(function () {
    if(playerTimerSeconds < 0) return;

    displayTime();

    playerTimerSeconds --;

    socket.send(JSON.stringify({ 
      'decrement-player-timer' : true 
    }))

  }, 1000);
}
function displayTime(){
  var hours   = parseInt((playerTimerSeconds / 3600) % 24, 10)
  var minutes = parseInt((playerTimerSeconds / 60) % 60, 10)
  var seconds = parseInt(playerTimerSeconds % 60, 10);
  hours   = hours   < 10 ? "0" + hours   : hours;
  minutes = minutes < 10 ? "0" + minutes : minutes;
  seconds = seconds < 10 ? "0" + seconds : seconds;
  document.querySelector('#player-timer').textContent = `Tempo: ${hours}:${minutes}:${seconds}`;
}



/* ----- Chat box event ----- */
/* -------------------------- */
document.querySelector("#chat-message-submit").addEventListener("click", function(){
  const messageInput = document.querySelector('#chat-message-input');
  const text = messageInput.value;
  socket.send(JSON.stringify({
    'chat-message-from': username,
    'chat-message-text': text
  }));
  messageInput.value = "";
})


/* ---------- Quit game ------ */
/* --------------------------- */
document.querySelector('#quit-game-modal').addEventListener('click', function(){
  socket.send(JSON.stringify({
    'quit-game-player' : username
  }));

  window.location.href = viewHome;
});


/* ---------- Quit room ------ */
/* --------------------------- */
document.querySelector('#quit-room').addEventListener('click', function(){
  socket.send(JSON.stringify({
    'quit-room' : true
  }));

  window.location.href = viewHome;
});