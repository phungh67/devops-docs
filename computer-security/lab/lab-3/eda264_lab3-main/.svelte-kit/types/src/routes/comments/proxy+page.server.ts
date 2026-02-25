// @ts-nocheck
import { json, error, redirect } from '@sveltejs/kit';

import {
	getUserFromSessionID,
	getComments,
	addComment
} from '$lib/db';

/** @param {Parameters<import('./$types').PageServerLoad>[0]} event */
export async function load({ cookies }) {
	const sessionid = cookies.get('sessionid');
	if (sessionid === undefined) redirect(307, '/');
	const user = getUserFromSessionID(sessionid);
	if (user !== undefined) {
		if (user.Error === undefined) {
			const comments = getComments();
			return { user, sessionid, comments };
		}
		else {
			cookies.delete('sessionid', { path: '/' });
			error(500, user.Error.message)
		}
	} else {
		cookies.delete('sessionid', { path: '/' });
		redirect(307, '/');
	}
}

/** */
export const actions = {
	comment:/** @param {import('./$types').RequestEvent} event */  async ({ cookies, request }) => {
		const data = await request.formData();
		const sid = cookies.get('sessionid');
		const message = data.get('message');
		const success = addComment(sid, message);
		if (success.done) {
			return { success: true };
		} else {
			if (success.Error !== undefined)
				error(500, success.Error.message)
			return { success: false };
		}
	}
};
