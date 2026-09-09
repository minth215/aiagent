package com.acme.member.service;

import com.acme.member.mapper.MemberMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

/**
 * 회원 가입 처리 서비스. 가입 시 중복 회원을 검사한 뒤 신규 회원을 등록한다.
 */
@Service
public class MemberService {

    @Autowired
    private MemberMapper memberMapper;

    public void registerMember(MemberVO vo) {
        if (memberMapper.countByMemberId(vo.getMemberId()) == 0) {
            memberMapper.insertMember(vo);
        }
    }
}
