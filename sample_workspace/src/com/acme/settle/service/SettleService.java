package com.acme.settle.service;

import java.util.List;

/**
 * 정산 업무 서비스 인터페이스.
 */
public interface SettleService {

    List<SettleVO> findSettleList();

    void applySettle(SettleVO vo);

    void approveSettle(SettleVO vo);
}
