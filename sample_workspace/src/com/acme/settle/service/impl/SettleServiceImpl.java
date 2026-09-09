package com.acme.settle.service.impl;

import com.acme.settle.mapper.SettleMapper;
import com.acme.settle.service.SettleService;
import com.acme.settle.service.SettleVO;
import java.util.List;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 정산 신청·승인 처리 로직 구현. 신청 시 대기상태로 저장하고,
 * 승인 시 상태를 변경한 뒤 회원 정산잔액을 갱신한다.
 */
@Service
public class SettleServiceImpl implements SettleService {

    @Autowired
    private SettleMapper settleMapper;

    @Override
    public List<SettleVO> findSettleList() {
        return settleMapper.selectSettleList();
    }

    @Override
    @Transactional
    public void applySettle(SettleVO vo) {
        vo.setStatus("REQUESTED");
        settleMapper.insertSettle(vo);
    }

    @Override
    @Transactional
    public void approveSettle(SettleVO vo) {
        vo.setStatus("APPROVED");
        settleMapper.updateSettleStatus(vo);
        settleMapper.updateMemberBalance(vo);
    }
}
