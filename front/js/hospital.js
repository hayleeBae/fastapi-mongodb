// const dataDepartment = document.querySelector();
// const dataLocation = document.querySelector();

function goToHospital(){
    $.ajax({
        type: 'GET',
        url: 'http://localhost:8080/hospital/find?department=내과&location=목동',
        // url: `http://localhost:8080/hospital/find?department=${내과}&location=${중랑구}`,
        dataType: 'json', 
        contentType: 'application/json',
        // data : {"hospitalMiddle" : "내과", "hospitalAddress" : "중랑구"}, //데이터 임시로 지정
        success: function (result) {
            localStorage.setItem('hospitalList', JSON.stringify(result))
            location.href='hospital.html'
        },
        error: function (result, status, error) {
            console.log(error)
        }
    });
}

const storedData = localStorage.getItem('hospitalList'); // 스토리지에 저장해둔 데이터, 
const hospitalResult = JSON.parse(storedData); //가져온 데이터를 javaScript객체로 변환
document.querySelector('#tbody').innerHTML = '';


let str = '';

for(let hospital of hospitalResult){
   // var positive = (hospital.positivePercentage) * 100;
    //alert(positive);

    str += '<tr>';
    // str += `    <td>${hospital.hospitalId}</td>`;
    str += `    <td><a onclick="hospitalInfo('${hospital.hospitalId}')">${hospital.hospitalName}</a></td>`;
    // str += `    <td><a onclick="test('${review.hospitalId}')" data-bs-toggle="modal" data-bs-target="#exampleModal">${review.hospitalName}</a></td>`;
    str += `    <td>${hospital.positivePercentage}%</td>`;
    str += `    <td>${hospital.negativePercentage}%</td>`;
    str += `    <td>${hospital.reviewTotalCnt}</td>`;

    str += '</tr>';
    str += '</tr>';

}



document.querySelector('#tbody').innerHTML = str;





//병원 이름 클릭 시 modal 실행
//pk가지고 와서 ajax로 데이터 조회 후 조회한 결과 모달안에 그려주기 
function hospitalInfo(hospitalId){
    //alert(hospitalId);
    $.ajax({
        type: 'GET',
        url: `http://localhost:8080/hospital/${hospitalId}`,
        dataType: 'json', 
        contentType: 'application/json',
        success: function(hospitalInfo) {
        console.log(hospitalInfo)
        
        let str = '';

        str += '<div id="map" style="width:100%; height: 350px;"></div>';
        str += '<div>';
        str += '    <table class="table">';
        str += '        <tbody>';
        str += '            <tr>';
        str += '            <th scope="row">주소</th>';
        str += `                <td>${hospitalInfo.hospitalAddress}</td>`;
        str += '            <tr>';
        str += '            <tr>';
        str += '            <th scope="row">전화번호</th>';
        str += `                <td>${hospitalInfo.hospitalTell}</td>`;
        str += '            <tr>';
        str += '            <tr>';
        str += '            <th scope="row">우편번호</th>';
        str += `                <td>${hospitalInfo.hospitalPost}</td>`;
        str += '            <tr>';


        let str2 = '';
        str2 += `<h2>${hospitalInfo.hospitalName}</h2>`

        document.querySelector('.modal-body').innerHTML = str;
        document.querySelector('#exampleModalLabel').innerHTML = str2;
        $("#exampleModal").modal("show");    

        },
        error: function (result, status, error) {
            console.log(error)
        }
    });


    
}