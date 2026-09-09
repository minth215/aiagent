<%@ page contentType="text/html; charset=UTF-8" %>
<html>
<head><title>회원 가입</title></head>
<body>
<h1>회원 가입</h1>
<form action="/member/join" method="post">
  <input type="text" name="memberId" placeholder="아이디"/>
  <input type="text" name="memberNm" placeholder="이름"/>
  <button type="submit">가입</button>
</form>
</body>
</html>
