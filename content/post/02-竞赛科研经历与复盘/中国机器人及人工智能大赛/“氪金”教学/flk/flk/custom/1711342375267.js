Blockly.Blocks['1711342375267'] = {
  init: function() {
    this.jsonInit({
      "type": "1711342375267",
      "message0": "sgt-q",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711342375267'] = function(block) {
  let code = "MOTOrigid16(60,60,60,30,60,60,60,30,60,60,60,30,60,60,60,30)\n\n\n-- 站立\nMOTOsetspeed(30)\nMOTOmove19(80,30,100,100,93,55,124,100,120,170,100,100,107,145,76,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(25)\nMOTOmove19(94,79,100,85,106,79,113,80,106,100,100,94,107,145,76,88,128,71,100)\nMOTOwait()\n\n\n-- 左腿上台阶\nMOTOsetspeed(15)\nMOTOmove19(97,105,100,85,132,127,85,89,103,100,100,94,107,145,76,88,128,71,100)\nMOTOwait()\nMOTOsetspeed(35)\nMOTOmove19(100,150,100,85,160,50,180,95,100,100,100,95,85,100,99,90,128,71,100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(100,150,100,93,160,76,154,98,100,100,100,100,135,150,99,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(100,100,100,100,160,78,155,100,100,100,100,100,145,150,99,100,128,71,100)\nMOTOwait()\nDelayMs(300)\nMOTOsetspeed(20)\nMOTOmove19(100,10,180,105,160,78,135,112,100,190,20,110,130,190,40,110,128,71,100)\nMOTOwait()\nDelayMs(100)\nMOTOsetspeed(30)\nMOTOmove19(100,10,180,105,115,65,125,112,100,190,20,115,155,180,105,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(100,10,180,105,115,65,125,112,100,190,20,111,110,68,163,99,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80,30,100,100,93,55,124,100,120,170,100,100,107,145,76,100,128,71,100)\nMOTOwait()\nDelayMs(100)\n";
  return code;
}

Blockly.Python['1711342375267'] = function(block) {
  let code = "robot.leju_action('sgt-q')\n";
  return code;
}

