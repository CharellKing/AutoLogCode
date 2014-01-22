AutoLogCode
===========

根据表来产生代码，例如：

货币变化日志表	log_data_moneychange
id	bigint	20	主键
accountid	bigint	20	帐号ID
username	varchar	32	用户名，data_account中的username
plyid	bigint	20	角色ID
nickname	varchar	32	角色昵称
plylevel	int	11	角色等级
moneytype	int	11	货币类型
changetype	int	11	货币变化类型
moneychange	int	11	货币变化量
moneyvalue	int	11	变化后货币剩余
viplevel	int	11	玩家vip等级
logdate	timestamp	0	日志记录时间
state	int	11	日志是否推送到综合后台的状态（默认为0未推送）

产生代码如下：

头文件：
//货币变化日志表
class LogDataMoneychange : public LogStruct {
public:
	static void Init (LogManager* m_pLogMgr);
	virtual std::string BuildInsertSql() const;

private:
	static LLong	id;//主键

public:
	LLong	accountid;//帐号ID
	string	username;//用户名，data_account中的username
	LLong	plyid;//角色ID
	string	nickname;//角色昵称
	int	plylevel;//角色等级
	int	moneytype;//货币类型
	int	changetype;//货币变化类型
	int	moneychange;//货币变化量
	int	moneyvalue;//变化后货币剩余
	int	viplevel;//玩家vip等级
	LLong	logdate;//日志记录时间
	int	state;//日志是否推送到综合后台的状态（默认为0未推送）
};


源文件:
LLong LogDataMoneychange::id = 0;

void LogDataMoneychange::Init (LogManager* pLogMgr) {
	id = pLogMgr->LoadLogSeq("log_data_moneychange" );
}

std::string LogDataMoneychange::BuildInsertSql()const {
	char sql[2048];
	snprintf(sql, 2047, "insert into log_data_moneychange (id, accountid, username, plyid, nickname, plylevel, moneytype, changetype, moneychange, moneyvalue, viplevel, logdate, state) values (%lld, %lld, %s, %lld, %s, %d, %d, %d, %d, %d, %d, FROM_UNIXTIME(%lld), %d)",
++id, accountid, username.c_str(), plyid, nickname.c_str(), plylevel, moneytype, changetype, moneychange, moneyvalue, viplevel, logdate, state);
	return std::string(sql);
}
