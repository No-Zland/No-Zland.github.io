Blockly.Blocks['1713949183398'] = {
  init: function() {
    this.jsonInit({
      "type": "1713949183398",
      "message0": "sgt-二阶-q",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1713949183398'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(80,30,100,100,93,55,124,100,120,170,100,100,107,145,76,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80,30,100,99,93,55,124,60,120,170,100,99,106,143,75,89,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(93,151,102,97,160,150,73,101,109,109,88,94,88,159,59,88,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(101,83,98,21,112,82,121,60,119,96,100,88,104,141,77,97,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(101,83,98,61,115,90,111,60,119,96,100,98,106,143,76,92,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(101,83,98,61,115,90,111,60,119,96,100,123,114,186,41,120,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(101,83,98,71,139,150,78,75,119,96,100,123,114,186,41,120,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(100,68,96,73,136,150,76,77,119,96,100,123,114,186,41,120,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(81,60,98,92,111,150,37,105,148,190,10,107,115,186,42,105,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(81,60,98,111,116,150,48,121,148,190,10,135,115,186,41,105,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(81,60,98,111,100,150,48,121,148,190,10,165,90,50,149,140,128,71,100)\nMOTOwait()\n\n\n-- 2右腿上台阶\nMOTOsetspeed(15)\nMOTOmove19(97,100,100,106,93,55,124,112,103,95,100,115,68,73,115,111,128,71,100)\nMOTOwait()\n\n\n-- 1\nMOTOsetspeed(35)\nMOTOmove19(100,100,100,105,115,100,101,110,100,50,100,115,40,150,20,105,128,71,100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(100,100,100,100,65,50,101,100,100,50,100,109,49,122,44,117,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(100,100,100,100,55,50,101,100,100,100,100,100,40,122,45,100,128,71,100)\nMOTOwait()\nDelayMs(300)\nMOTOsetspeed(20)\nMOTOmove19(100,10,180,90,70,10,160,90,100,190,20,95,40,122,65,88,128,71,100)\nMOTOwait()\nDelayMs(100)\nMOTOsetspeed(30)\nMOTOmove19(100,10,180,85,45,20,95,100,100,190,20,95,85,135,75,88,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(100,10,180,85,130,90,105,100,100,190,20,95,95,135,75,88,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80,30,100,100,93,55,124,100,120,170,100,100,107,145,76,100,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1713949183398'] = function(block) {
  let code = "robot.leju_action('sgt-二阶-q')\n";
  return code;
}

