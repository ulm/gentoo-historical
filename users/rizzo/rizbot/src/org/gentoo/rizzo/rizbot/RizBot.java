/* vim: set expandtab tabstop=4 shiftwidth=4 softtabstop=4: */
/**
 * RizBot.  An extenion of a lot of jibble bots (http://www.jibble.org)
 * 
 * Copyright (c) 2005 Don Seiler, rizzo@gentoo.org
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *·
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *·
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

package org.gentoo.rizzo.rizbot;

import org.jibble.pircbot.*;
import org.jibble.jmegahal.*;
import org.jibble.socnet.*;
import org.jibble.reminderbot.*;

import java.util.*;
import java.util.regex.*;
import java.awt.image.BufferedImage;
import java.io.*;

/**
 * RizBot extends PircBot to connect to IRC.  It duplicates PieSpy, and adds
 * JMegaHal and ReminderBot features.
 *
 * $Id: RizBot.java,v 1.4 2005/03/15 21:49:10 rizzo Exp $
 */
public class RizBot extends PircBot implements Runnable {

    public static final String VERSION = "RizBot 0.1.0";
    private static final String REMINDER_FILE = "reminders.dat";
    private JMegaHal hal;

    public RizBot(Configuration config) throws IOException {
        this.config = config;

        // Prevent construction if the output directory does not exist.
        if (!config.outputDirectory.exists() || !config.outputDirectory.isDirectory()) {
            throw new IOException("Output directory (" + config.outputDirectory + ") does not exist.");
        }

        File file = new File("brain.ser");
        try {
            ObjectInputStream in = new ObjectInputStream(new FileInputStream(file));
            hal = (JMegaHal)in.readObject();
            in.close();
        } catch (Exception e) {
            hal = new JMegaHal();
            try {
                hal.addDocument("file:///home/dseiler/cvs/gentoo/gentoo/users/rizzo/rizbot/h2g2_dialogue.txt");
            } catch (FileNotFoundException e2) {
            }
        }


        dispatchThread = new Thread(this);
        dispatchThread.start();
    }

    // Overriden from PircBot.    
    public void onMessage(String channel, String sender, String login,
                                            String hostname, String message) {

        // JMegaHal parsing
        if (message.toLowerCase().indexOf(getNick().toLowerCase()) >= 0) {
            // If the bot's nickname was mentioned, generate a random reply
            String sentence = hal.getSentence();
            sendMessage(channel, sentence);
        } else if (message.equalsIgnoreCase("!save")) {
            // Save the brain
            try {
                ObjectOutput out = new ObjectOutputStream(new FileOutputStream("brain.ser"));
                out.writeObject(hal);
                out.close();
            } catch (FileNotFoundException e) {
            } catch (IOException e) {
            }
        } else {
            // Otherwise, make the bot learn the message
            hal.add(message);
        }

        // PieSpy parsing
        if (config.ignoreSet.contains(sender.toLowerCase())) {
            return;
        }

        add(channel, sender);

        // Pass the message on to the InferenceHeuristics in the channel's Graph.
        String key = channel.toLowerCase();
        Graph graph = (Graph) _graphs.get(key);
        graph.infer(sender, Colors.removeFormattingAndColors(message));

        // Reminder parsing
        Pattern messagePattern = Pattern.compile("^\\s*(?i:(" + getNick() + ")?\\s*[\\:,]?\\s*remind\\s+me\\s+in\\s+(((\\d+\\.?\\d*|\\.\\d+)\\s+(weeks?|days?|hours?|hrs?|minutes?|mins?|seconds?|secs?)[\\s,]*(and)?\\s+)+)(.*)\\s*)$");
        Matcher m = messagePattern.matcher(message);
        if (m.matches()) {
            String reminderMessage = m.group(7);
            String periods = m.group(2);

            long set = System.currentTimeMillis();
            long due = set;

            try {
                double weeks = getPeriod(periods, "weeks|week");
                double days = getPeriod(periods, "days|day");
                double hours = getPeriod(periods, "hours|hrs|hour|hr");
                double minutes = getPeriod(periods, "minutes|mins|minute|min");
                double seconds = getPeriod(periods, "seconds|secs|second|sec");
                due += (weeks * 604800 + days * 86400 + hours * 3600 + minutes * 60 + seconds) * 1000;
            }
            catch (NumberFormatException e) {
                sendMessage(channel, sender + ": I can't quite deal with numbers like that!");
                return;
            }

            if (due == set) {
                sendMessage(channel, "Example of correct usage: \"Remind me in 1 hour, 10 minutes to check the oven.\"  I understand all combinations of weeks, days, hours, minutes and seconds.");
                return;
            }

            Reminder reminder = new Reminder(channel, sender, reminderMessage, set, due);
            sendMessage(channel, sender + ": Okay, I'll remind you about that on " + new Date(reminder.getDueTime()));
            reminders.add(reminder);
            dispatchThread.interrupt();
        }

    }

    public double getPeriod(String periods, String regex) throws NumberFormatException {
        Pattern pattern = Pattern.compile("^.*?([\\d\\.]+)\\s*(?i:(" + regex + ")).*$");
        Matcher m = pattern.matcher(periods);
        m = pattern.matcher(periods);
        if (m.matches()) {
            double d = Double.parseDouble(m.group(1));
            if (d < 0 || d > 1e6) {
                throw new NumberFormatException("Number too large or negative (" + d + ")");
            }
            return d;
        }
        return 0;
    }


    // Overriden from PircBot. Private messages can control the bot.
    protected void onPrivateMessage(String sender, String login,
                                            String hostname, String message) {
        // Only allow access if the correct password has been supplied.
        if (!message.startsWith(config.password)) {
            sendMessage(sender, "Incorrect password.");
            return;
        }

        message = message.substring(config.password.length()).trim();
        String messageLc = message.toLowerCase();

        if (messageLc.equals("stats")) {
            // Tell the user about the Graphs currently stored.
            Iterator keyIt = _graphs.keySet().iterator();
            while (keyIt.hasNext()) {
                String key = (String) keyIt.next();
                Graph graph = (Graph) _graphs.get(key);
                sendMessage(sender, key + ": " + graph.toString());
            }
        }
        else if (messageLc.startsWith("raw ")) {
            // Send a raw line to the IRC server.
            sendRawLine(message.substring(4));
        }
        else if (messageLc.startsWith("join ")) {
            // Join a new channel.
            joinChannel(message.substring(5));
        }
        else if (messageLc.startsWith("part ")) {
            // Part the specified channel.
            String channel = message.substring(5);
            partChannel(channel);
            _channelSet.remove(channel.toLowerCase());
        }
        else if (messageLc.startsWith("ignore ") || messageLc.startsWith("remove ")) {
            // Add a user to the IgnoreSet and remove them from all Graphs.
            String nick = message.substring(7);
            config.ignoreSet.add(nick.toLowerCase());
            Iterator graphIt = _graphs.values().iterator();
            while (graphIt.hasNext()) {
                Graph g = (Graph) graphIt.next();
                boolean changed = g.removeNode(new Node(nick));
                if (changed) {
                    g.makeNextImage();
                }
            }
        }
        else if (messageLc.startsWith("draw ")) {
            // DCC SEND the latest file for a channel.
            StringTokenizer tokenizer = new StringTokenizer(message.substring(5));
            if (tokenizer.countTokens() >= 1) {
                String channel = tokenizer.nextToken();

                Graph graph = (Graph) _graphs.get(channel.toLowerCase());
                if (graph != null) {
                    try {
                        File file = (File) graph.getLastFile();
                        if (file != null) {
                            sendMessage(sender, "Trying to send \"" + file.getName() + "\"... If you have difficultly in recieving this file via DCC, there may be a firewall between us.");
                            dccSendFile(file, sender, 120000);
                        } else {
                            sendMessage(sender, "I have not generated any images for " + channel + " yet.");
                        }
                    } catch (Exception e) {
                        sendMessage(sender, "Sorry, mate: " + e.toString());
                    }
                } else {
                    sendMessage(sender, "Sorry, I don't know much about that channel yet.");
                }
            } else {
                sendMessage(sender, "Example of correct use is \"draw <#channel>\"");
            }
        } else {
            sendMessage(sender, "Sorry, I don't support that command yet.");
        }
    }

    // Overridden from PircBot. Treat channel actions as messages.
    protected void onAction(String sender, String login, String hostname, String target, String action) {
        if ("#&!+".indexOf(target.charAt(0)) >= 0) {
            onMessage(target, sender, login, hostname, action);
        }
    }

    // Overridden from PircBot.    
    protected void onJoin(String channel, String sender, String login, String hostname) {

        add(channel, sender);

        if (sender.equalsIgnoreCase(getNick())) {
            // Remember that we're meant to be in this channel
            _channelSet.add(channel.toLowerCase());
        }
    }

    // Overridden from PircBot.
    protected void onUserList(String channel, User[] users) {
        for (int i = 0; i < users.length; i++) {
            add(channel, users[i].getNick());
        }
    }

    // Overridden from PircBot.
    protected void onKick(String channel, String kickerNick, String kickerLogin,
                        String kickerHostname, String recipientNick, String reason) {
        add(channel, kickerNick);
        add(channel, recipientNick);

        if (recipientNick.equalsIgnoreCase(getNick())) {
            // The bot was kicked, so rejoin the channel (if possible).
            joinChannel(channel);
        }
    }

    // Overridden from PircBot.
    protected void onMode(String channel, String sourceNick, String sourceLogin,
                                                String sourceHostname, String mode) {
        add(channel, sourceNick);
    }

    // Overridden from PircBot.
    protected void onNickChange(String oldNick, String login, String hostname,
                                                                    String newNick) {
        changeNick(oldNick, newNick);
    }

    // Overridden from PircBot.
    public void onDisconnect() {
        while (!isConnected()) {
            try {
                reconnect();
            }
            catch (Exception e) {
                try {
                    Thread.sleep(10*60*1000);
                }
                catch (InterruptedException ie) {
                    // do nothing
                }
            }
        }

        // We are now connected. Rejoin all channels.
        Iterator it = _channelSet.iterator();
        while (it.hasNext()) {
            joinChannel((String) it.next());
        }
    }

    private void add(String channel, String nick) {

        if (config.ignoreSet.contains(nick.toLowerCase())) {
            return;
        }

        Node node = new Node(nick);
        String key = channel.toLowerCase();

        // Create the Graph for this channel if it doesn't already exist.
        Graph graph = (Graph) _graphs.get(key);
        if (graph == null) {
            if (config.createRestorePoints) {
                graph = readGraph(key);
            }
            if (graph == null) {
                graph = new Graph(channel, config);
            }
            _graphs.put(key, graph);
        }

        // Add the Node to the Graph.
        graph.addNode(node);
    }

    private void changeNick(String oldNick, String newNick) {
        // Effect the nick change by calling the mergeNode method on all Graphs.
        Iterator graphIt = _graphs.values().iterator();
        while (graphIt.hasNext()) {
            Graph graph = (Graph) graphIt.next();
            Node oldNode = new Node(oldNick);
            Node newNode = new Node(newNick);
            graph.mergeNode(oldNode, newNode);
        }
    }

    // Read a serialized graph from disk.
    private Graph readGraph(String channel) {
        Graph g = null;
        // Try and see if the graph can be restored from file.
        try {
            String strippedChannel = channel.toLowerCase().substring(1);

            File dir = new File(config.outputDirectory, strippedChannel);
            File file = new File(dir, strippedChannel + "-restore.dat");
            ObjectInputStream ois = new ObjectInputStream(new FileInputStream(file));
            String version = (String) ois.readObject();
            if (version.equals(RizBot.VERSION)) {
                // Only read the object if the file is for the correct version.
                g = (Graph) ois.readObject();
            }
            ois.close();
        }
        catch (Exception e) {
            // Do nothing?
        }
        return g;
    }

    public Configuration getConfig() {
        return config;
    }

    public Graph getGraph(String channel) {
        channel = channel.toLowerCase();
        return (Graph) _graphs.get(channel);
    }

    public static void main(String[] args) throws Exception {

        Properties p = new Properties();
        String configFile = "./config.ini";
        if (args.length > 0) {
            configFile = args[0];
        }
        p.load(new FileInputStream(configFile));
        Configuration config = new Configuration(p);

        RizBot bot = new RizBot(config);
        bot.setVerbose(config.verbose);
        bot.setName(config.nick);
        bot.setLogin("rizbot");
        bot.setVersion(VERSION + " http://dev.gentoo.org/~rizzo/rizbot/");

        try {
            bot.setEncoding(config.encoding);
        }
        catch (UnsupportedEncodingException e) {
            // Stick with the platform default.
        }

        bot.connect(config.server, config.port, config.serverPassword);
        Iterator channelIt = config.channelSet.iterator();
        while (channelIt.hasNext()) {
            String channel = (String) channelIt.next();
            bot.joinChannel(channel);
        }
    }


    public synchronized void run() {
        boolean running = true;
        while (running) {

            // If the list is empty, wait until something gets added.
            if (reminders.size() == 0) {
                try {
                    wait();
                }
                catch (InterruptedException e) {
                    // Do nothing.
                }
            }

            Reminder reminder = (Reminder) reminders.getFirst();
            long delay = reminder.getDueTime() - System.currentTimeMillis();
            if (delay > 0) {
                try {
                    wait(delay);
                }
                catch (InterruptedException e) {
                    // A new Reminder was added. Sort the list.
                    Collections.sort(reminders);
                    saveReminders();
                }
            }
            else {
                sendMessage(reminder.getChannel(), reminder.getNick() + ": You asked me to remind you " + reminder.getMessage());
                reminders.removeFirst();
                saveReminders();
            }
        }
    }


    private void saveReminders() {
        try {
            ObjectOutputStream out = new ObjectOutputStream(new FileOutputStream(new File(REMINDER_FILE)));
            out.writeObject(reminders);
            out.flush();
            out.close();
        }
        catch (Exception e) {
            // If it doesn't work, no great loss!
        }
    }

    private void loadReminders() {
        try {
            ObjectInputStream in = new ObjectInputStream(new FileInputStream(new File(REMINDER_FILE)));
            reminders = (LinkedList) in.readObject();
            in.close();
        }
        catch (Exception e) {
            // If it doesn't work, no great loss!
        }
    }


    // HashMap of String -> Graph objects.
    private HashMap _graphs = new HashMap();

    // Used to remember which channels we should be in
    private HashSet _channelSet = new HashSet();

    private Thread dispatchThread;
    private LinkedList reminders = new LinkedList();

    private Configuration config;

}
