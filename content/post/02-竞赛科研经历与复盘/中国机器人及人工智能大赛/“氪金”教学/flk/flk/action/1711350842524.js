Blockly.Blocks['1711350842524'] = {
  init: function() {
    this.jsonInit({
      "type": "1711350842524",
      "message0": "sgt-j",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711350842524'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(20)\nMOTOmove19(80,30,100,101,131,150,60,102,120,170,100,102,70,50,138,103,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(101,101,101,95,120,119,85,95,135,104,99,105,80,81,115,105,128,71,100)\nMOTOwait()\nMOTOsetspeed(25)\nMOTOmove19(145,155,105,90,132,138,75,108,55,45,95,105,75,85,108,117,128,71,100)\nMOTOwait()\nMOTOsetspeed(35)\nMOTOmove19(145,155,105,78,130,138,75,110,55,45,95,110,70,62,125,111,128,71,100)\nMOTOwait()\n\n\n-- 4\nMOTOsetspeed(28)\nMOTOmove19(100,75,100,50,130,138,75,80,45,33,95,150,70,62,125,111,128,71,100)\nMOTOwait()\n\n\n-- 5\nMOTOsetspeed(28)\nMOTOmove19(80,30,100,100,93,55,124,100,120,170,100,100,107,145,76,100,128,71,100)\nMOTOwait()\n\n\n-- 6\nMOTOsetspeed(35)\nMOTOmove19(80,30,100,108,93,55,124,100,120,170,100,92,107,145,76,100,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711350842524'] = function(block) {
  let code = "robot.leju_action('sgt-j')\n";
  return code;
}

