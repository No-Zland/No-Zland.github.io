Blockly.Blocks['1749030041381'] = {
  init: function() {
    this.jsonInit({
      "type": "1749030041381",
      "message0": "起立",
      "previousStatement": "motion_block",
      "nextStatement": "motion_block",
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1749030041381'] = function(block) {
  let code = "MOTOrigid16(60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60)\nMOTOsetspeed(80)\nMOTOmove19(93,100,20,101,131,126,170,100,108,100,185,99,69,74,30,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(92,16,46,100,80,150,60,100,108,184,154,100,120,50,140,100,128,71,100)\nMOTOwait()\nDelayMs(10)\nMOTOsetspeed(80)\nMOTOmove19(92,18,58,100,73,150,40,100,108,182,142,100,127,50,160,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(50)\nMOTOmove19(92,25,135,100,124,150,50,100,108,175,65,100,76,50,150,100,128,71,100)\nMOTOwait()\nDelayMs(50)\nMOTOsetspeed(20)\nMOTOmove19(80,30,100,100,93,55,124,100,120,170,100,100,107,145,76,100,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1749030041381'] = function(block) {
  let code = "robot.leju_action('起立')\n";
  return code;
}

