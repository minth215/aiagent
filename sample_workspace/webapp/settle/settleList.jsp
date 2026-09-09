<%@ page contentType="text/html; charset=UTF-8" %>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<html>
<head><title>정산 목록</title></head>
<body>
<h1>정산 신청 목록</h1>
<table>
  <tr><th>정산ID</th><th>회원</th><th>금액</th><th>상태</th></tr>
  <c:forEach var="row" items="${items}">
    <tr>
      <td>${row.settleId}</td><td>${row.memberNm}</td>
      <td>${row.amount}</td><td>${row.status}</td>
    </tr>
  </c:forEach>
</table>
<form action="/settle/apply" method="post">
  <input type="text" name="memberId"/>
  <input type="text" name="amount"/>
  <button type="submit">정산 신청</button>
</form>
</body>
</html>
