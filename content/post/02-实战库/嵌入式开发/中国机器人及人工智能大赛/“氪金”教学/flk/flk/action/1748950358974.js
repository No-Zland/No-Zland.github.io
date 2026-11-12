Blockly.Blocks['1748950358974'] = {
  init: function() {
    this.jsonInit({
      "type": "1748950358974",
      "message0": "gaotaifangkuai",
      "previousStatement": "motion_block",
      "nextStatement": "motion_block",
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1748950358974'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(75,10,169,100,93,55,130,98,122,190,31,100,107,145,70,102,120,40,100)\nMOTOwait()\n\n\n-- 1\nMOTOsetspeed(15)\nMOTOmove19(80,10,156,105,119,150,49,103,135,179,44,107,88,50,160,105,120,40,99)\nMOTOwait()\nDelayMs(5)\nMOTOsetspeed(30)\nMOTOmove19(79,10,138,104,114,148,41,102,133,178,56,105,85,51,162,104,120,40,99)\nMOTOwait()\nMOTOsetspeed(50)\nMOTOmove19(78,32,137,104,114,148,41,102,134,148,56,105,85,51,162,104,120,40,99)\nMOTOwait()\nMOTOsetspeed(50)\nMOTOmove19(77,34,55,103,109,150,42,102,134,142,153,105,93,50,161,105,120,40,99)\nMOTOwait()\nMOTOsetspeed(25)\nMOTOmove19(80,30,100,100,93,55,124,100,120,170,100,100,107,145,76,100,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1748950358974'] = function(block) {
  let code = "robot.leju_action('gaotaifangkuai')\n";
  return code;
}

