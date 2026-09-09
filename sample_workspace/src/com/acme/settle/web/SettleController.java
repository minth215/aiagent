package com.acme.settle.web;

import com.acme.settle.service.SettleService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;

/**
 * 정산 신청/승인 화면 요청을 처리하는 컨트롤러.
 */
@Controller
@RequestMapping("/settle")
public class SettleController {

    @Autowired
    private SettleService settleService;

    @GetMapping("/list")
    public String list(Model model) {
        model.addAttribute("items", settleService.findSettleList());
        return "settle/settleList";
    }

    @PostMapping("/apply")
    public String apply(SettleVO vo) {
        settleService.applySettle(vo);
        return "redirect:/settle/list";
    }

    @PostMapping("/approve")
    public String approve(SettleVO vo) {
        settleService.approveSettle(vo);
        return "redirect:/settle/list";
    }
}
