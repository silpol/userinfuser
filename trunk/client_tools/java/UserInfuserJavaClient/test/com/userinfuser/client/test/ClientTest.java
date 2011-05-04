package com.userinfuser.client.test;

import java.io.IOException;

import com.userinfuser.client.UserInfuser;
import com.userinfuser.client.WidgetType;

public class ClientTest
{
	
	private final static String USER_ID_1 = "shanaccount_user1";
	private final static String USER_ID_2 = "shanaccount_user2";
	private final static String USER_ID_3 = "shanaccount_user3";
	private final static String USER_ID_4 = "shanaccount_user4";
	private final static String USER_ID_5 = "shanaccount_user5";
	private final static String USER_ID_6 = "shanaccount_user6";
	
	private final static String ACCOUNT_ID = "shanrandhawa@gmail.com";
	private final static String API_KEY = "72db2679-f82f-426b-9299-bb5c2eac0dcd";
	
	private static UserInfuser f_userInfuserModule;
	
	private static void createUserAccounts() throws IOException
	{
		// Create users in target account
		f_userInfuserModule.updateUser(USER_ID_4);
		f_userInfuserModule.updateUser(USER_ID_5);
		f_userInfuserModule.updateUser(USER_ID_6);
	}
	
	public static void main(String[] args) throws IOException
	{
		// TODO Auto-generated method stub
		f_userInfuserModule = new UserInfuser(ACCOUNT_ID, API_KEY, false, false, false, true);
		
		// createUserAccounts();
		
		String user1Info = f_userInfuserModule.getUserInfo(USER_ID_2);
		System.out.println("UserInfo: " + user1Info);
		
		//f_userInfuserModule.awardPoints(USER_ID_4, 100);
		//f_userInfuserModule.awardPoints(USER_ID_5, 100);
		//f_userInfuserModule.awardPoints(USER_ID_6, 100);
		//f_userInfuserModule.awardBadge(USER_ID_4, "Shan-Shan the DON-private");
		f_userInfuserModule.awardBadgePoints(USER_ID_1, 4800, "coolguy-newbadge-private", 5000);
		//f_userInfuserModule.awardPoints(USER_ID_1, 1000);
		
		// attempt to get the widget
		final String widgetHTML = f_userInfuserModule.getWidget(USER_ID_1, WidgetType.TROPHY_CASE, 500, 500);
		System.out.println("THE WIDGET HTML:\n" + widgetHTML);
		
	}
	
}
