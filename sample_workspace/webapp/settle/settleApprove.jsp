<%@ page contentType="text/html; charset=UTF-8" %>
<html>
<head><title>정산 승인</title></head>
<body>
<h1>정산 승인</h1>
<form action="/settle/approve" method="post">
  <input type="hidden" name="settleId" value="${settleId}"/>
  <button type="submit">승인</button>
</form>
</body>
</html>
