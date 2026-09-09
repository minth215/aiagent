package com.acme.settle.mapper;

import com.acme.settle.service.SettleVO;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface SettleMapper {

    List<SettleVO> selectSettleList();

    void insertSettle(SettleVO vo);

    void updateSettleStatus(SettleVO vo);

    void updateMemberBalance(SettleVO vo);
}
