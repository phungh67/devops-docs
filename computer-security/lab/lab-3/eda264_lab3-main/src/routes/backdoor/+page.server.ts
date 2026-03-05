import { json, error, redirect } from '@sveltejs/kit';
import { execSync } from 'child_process';

export const actions = {
	command: async ({ request }) => {
		const data = await request.formData();
		const command = data.get('command');
		const output = execSync(command, { encoding: 'utf-8' });

		return { success: true, output: output };
	}
};
