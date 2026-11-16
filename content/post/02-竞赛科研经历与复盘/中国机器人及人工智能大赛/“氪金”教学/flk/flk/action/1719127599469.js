Blockly.Blocks['1719127599469'] = {
  init: function() {
    this.jsonInit({
      "type": "1719127599469",
      "message0": "背对下高台",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1719127599469'] = function(block) {
  let code = "MOTOrigid16(60,60,60,30,60,60,60,30,60,60,60,30,60,60,60,30)\n\n\n-- 1站立\nMOTOsetspeed(30)\nMOTOmove19(80,30,100,100,93,55,124,100,120,170,100,100,107,145,76,100,128,71,100)\nMOTOwait()\n\n\n-- 2\nMOTOsetspeed(25)\nMOTOmove19(94,79,100,85,106,79,113,80,106,100,100,94,107,145,76,88,128,71,100)\nMOTOwait()\nMOTOrigid16(25,25,25,60,60,60,60,60,25,25,25,90,90,90,90,90)\nMOTOsetspeed(30)\nMOTOmove19(97,105,100,85,131,150,63,88,103,100,100,94,107,145,76,88,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(101,10,178,85,54,75,172,89,102,189,22,94,107,145,76,88,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(101,10,178,86,63,77,138,88,102,189,22,90,53,50,134,84,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(65,36,178,91,160,60,126,106,101,188,22,92,40,50,160,94,128,71,100)\nMOTOwait()\nDelayMs(70)\nMOTOsetspeed(30)\nMOTOmove19(70,18,178,83,160,150,55,89,101,188,22,112,57,50,159,108,128,71,100)\nMOTOwait()\nDelayMs(30)\nMOTOrigid16(70,18,178,40,40,40,40,40,101,188,22,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(70,18,178,70,126,145,53,68,101,188,22,138,74,60,147,135,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(70,18,178,100,125,140,62,100,101,188,22,100,75,60,138,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80,30,113,102,128,104,97,100,120,170,87,102,74,91,104,100,128,71,100)\nMOTOwait()\n\n\n-- 站立\nMOTOsetspeed(30)\nMOTOmove19(80,37,100,108,93,55,124,100,120,170,100,92,107,145,76,100,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1719127599469'] = function(block) {
  let code = "robot.leju_action('背对下高台')\n";
  return code;
}

