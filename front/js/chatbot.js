const storedData = localStorage.getItem('userId');
const userIdResult = JSON.parse(storedData);
//alert(userIdResult);
document.querySelector('#user').innerHTML = `${userIdResult}님 반갑습니다`;

document.addEventListener('DOMContentLoaded', function() {
  var messageInput = document.getElementById('message-input');
  messageInput.addEventListener('keypress', function(event) {
      if (event.key === 'Enter') {
          sendMessage();
      }
  });
});

function sendMessage() {
  var messageInput = document.getElementById('message-input');
  var chatBox = document.getElementById('chat-box');

  if (messageInput.value.trim() !== '') {
    // 나의 메시지
    chatBox.innerHTML += '<div class="message my-message"><strong>나:</strong> ' + messageInput.value + '</div>';
    userMsg = messageInput.value;
    messageInput.value = '';

   $.ajax({
        url: 'http://127.0.0.1:8000/chatbot/',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ "utterance": userMsg, "gu": "중랑구" }),
     success: function (data) {
          console.log(data)
          appendMessage('의료진단AI', data.bot_message, 'other-message');
        },
        error: function (error) {
          console.error('Error:', error);
          appendMessage('의료진단AI', '오류가 발생했습니다.', 'other-message');
        }
      });

    // 상대의 응답 (임의로 "상대"로 고정된 메시지)
    // setTimeout(function() {
    //   chatBox.innerHTML += '<div class="message other-message"><strong>상대:</strong> 안녕하세요!</div>';



    //   // chatBox.innerHTML += '<div class="message other-message">';
    //   // chatBox.innerHTML += '    <strong>';
    //   // chatBox.innerHTML += '        <img src="/images/doctor.png" alt="" width="50">';
    //   // chatBox.innerHTML += '     </strong>';
    //   // chatBox.innerHTML += '</div>';

    //   chatBox.scrollTop = chatBox.scrollHeight; // 스크롤을 항상 아래로 조정
    // }, 500); // 0.5초 후에 응답이 오도록 설정 (시뮬레이션용)
  }
}

function appendMessage(sender, message, messageType) {
      var chatBox = document.getElementById('chat-box');
      chatBox.innerHTML += '<div class="message ' + messageType + '"><strong>' + sender + ':</strong> ' + message + '</div>';
      chatBox.scrollTop = chatBox.scrollHeight;
    }

// myModal.addEventListener('shown.bs.modal', () => {
//   myInput.focus()
// })

// $('#testBtn').click(function(e){
//     e.preventDefault();
//     $('#testModal').modal("show");
// });






// const chatbotBtn = document.getElementById('chatbotBtn');
//  var department = document.getElementById('department').value;

// chatbotBtn.addEventListener('click', (event) => {
//     event.preventDefault();
//     // alert(department);

//         $.ajax({
//             type: 'GET',
//             url: 'http://localhost:8080/hospital',
//             // dataType: 'json', // 서버에서 준 데이터 형식
//            // contentType: 'application/json',
//           //  data: JSON.stringify(loginDto),
//             data : {"department" : "내과"},
//             success: function (result) {
//                 console.log(result)
//                 alert(result)


//             },
//             error: function (result, status, error) {
//                 console.log(error)
//             }
//         });
//  });